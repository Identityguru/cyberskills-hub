import hashlib
import io
import json
import os
import zipfile
from pathlib import Path

import markdown
import yaml
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_auth
from app.config import settings
from app.database import get_db
from app import models

router = APIRouter(tags=["skills"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

CATEGORIES = [
    "Detection & Analysis",
    "Investigation & Forensics",
    "Defense & Hardening",
    "Response & Remediation",
    "Testing & Validation",
    "Identity & Access Management",
]

VENDORS = ["okta", "sailpoint", "cyberark", "community"]


def _skill_to_dict(skill: models.Skill) -> dict:
    return {
        "id": skill.id,
        "slug": skill.slug,
        "name": skill.name,
        "description": skill.description,
        "category": skill.category,
        "subcategory": skill.subcategory,
        "vendor": skill.vendor,
        "tags": skill.tags,
        "mitre_attack_ids": skill.mitre_attack_ids,
        "version": skill.version,
        "download_count": skill.download_count,
        "status": skill.status,
        "readme_html": markdown.markdown(skill.readme_content or "", extensions=["fenced_code", "tables"]),
        "readme_content": skill.readme_content,
        "created_at": skill.created_at,
        "author_username": skill.author.username if skill.author else "CyberSkills Hub",
    }


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total_skills = db.query(models.Skill).filter(models.Skill.status == "approved").count()
    total_downloads = db.query(models.Download).count()
    total_contributors = db.query(models.User).count()
    featured = db.query(models.Skill).filter(models.Skill.status == "approved").order_by(
        models.Skill.download_count.desc()
    ).limit(6).all()
    vendor_counts = {}
    for v in VENDORS[:-1]:
        vendor_counts[v] = db.query(models.Skill).filter(
            models.Skill.vendor == v, models.Skill.status == "approved"
        ).count()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "total_skills": total_skills,
        "total_downloads": total_downloads,
        "total_contributors": total_contributors,
        "featured_skills": [_skill_to_dict(s) for s in featured],
        "vendor_counts": vendor_counts,
        "categories": CATEGORIES,
    })


@router.get("/skills", response_class=HTMLResponse)
def skills_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    vendor: str = "",
    category: str = "",
    q: str = "",
):
    query = db.query(models.Skill).filter(models.Skill.status == "approved")
    if vendor:
        query = query.filter(models.Skill.vendor == vendor)
    if category:
        query = query.filter(models.Skill.category == category)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Skill.name.ilike(like) |
            models.Skill.description.ilike(like) |
            models.Skill._tags.ilike(like)
        )
    skills = query.order_by(models.Skill.download_count.desc()).all()
    return templates.TemplateResponse("skills/list.html", {
        "request": request,
        "current_user": current_user,
        "skills": [_skill_to_dict(s) for s in skills],
        "categories": CATEGORIES,
        "vendors": VENDORS,
        "active_vendor": vendor,
        "active_category": category,
        "search_query": q,
        "total_count": len(skills),
    })


@router.get("/skills/upload", response_class=HTMLResponse)
def upload_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("skills/upload.html", {
        "request": request,
        "current_user": current_user,
        "categories": CATEGORIES,
        "vendors": VENDORS,
    })


@router.post("/skills/upload")
async def upload_skill(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
    skill_file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    vendor: str = Form(...),
    tags: str = Form(""),
    mitre_ids: str = Form(""),
    version: str = Form("1.0"),
):
    content = await skill_file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return templates.TemplateResponse("skills/upload.html", {
            "request": request, "current_user": current_user,
            "error": "File must be a UTF-8 text file (SKILL.md).",
            "categories": CATEGORIES, "vendors": VENDORS,
        })

    slug = name.lower().replace(" ", "-").replace("_", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    if db.query(models.Skill).filter(models.Skill.slug == slug).first():
        slug = f"{slug}-{current_user.id}"

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    mitre_list = [m.strip() for m in mitre_ids.split(",") if m.strip()]

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{slug}/SKILL.md", text)
    zip_buf.seek(0)

    vendor_dir = Path(settings.skills_data_dir) / (vendor if vendor in VENDORS else "community")
    vendor_dir.mkdir(parents=True, exist_ok=True)
    zip_path = vendor_dir / f"{slug}.zip"
    zip_path.write_bytes(zip_buf.getvalue())

    skill = models.Skill(
        slug=slug,
        name=name,
        description=description,
        category=category,
        vendor=vendor if vendor in VENDORS else "community",
        version=version,
        author_id=current_user.id,
        status="pending",
        file_path=str(zip_path),
        readme_content=text,
    )
    skill.tags = tag_list
    skill.mitre_attack_ids = mitre_list
    db.add(skill)
    db.commit()

    return RedirectResponse(url=f"/skills/{skill.slug}", status_code=302)


@router.get("/skills/{slug}", response_class=HTMLResponse)
def skill_detail(slug: str, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    skill = db.query(models.Skill).filter(models.Skill.slug == slug).first()
    if not skill or (skill.status != "approved" and (not current_user or current_user.role != "admin")):
        raise HTTPException(status_code=404, detail="Skill not found")
    related = db.query(models.Skill).filter(
        models.Skill.vendor == skill.vendor,
        models.Skill.status == "approved",
        models.Skill.slug != slug,
    ).limit(4).all()
    return templates.TemplateResponse("skills/detail.html", {
        "request": request,
        "current_user": current_user,
        "skill": _skill_to_dict(skill),
        "related_skills": [_skill_to_dict(s) for s in related],
    })


@router.get("/skills/{slug}/download")
def download_skill(slug: str, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    skill = db.query(models.Skill).filter(models.Skill.slug == slug, models.Skill.status == "approved").first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
    dl = models.Download(skill_id=skill.id, user_id=current_user.id if current_user else None, ip_hash=ip_hash)
    db.add(dl)
    skill.download_count += 1
    db.commit()

    zip_path = Path(skill.file_path)
    if not zip_path.exists():
        # Regenerate zip from stored readme_content
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{slug}/SKILL.md", skill.readme_content or "")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{slug}.zip"'},
        )

    def iter_file():
        with open(zip_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iter_file(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{slug}.zip"'},
    )


@router.get("/categories/{category}", response_class=HTMLResponse)
def category_page(category: str, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return RedirectResponse(url=f"/skills?category={category}", status_code=302)
