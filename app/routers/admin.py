from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import require_admin, hash_password
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


# ── Dashboard ────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    pending = db.query(models.Skill).filter(models.Skill.status == "pending").all()
    approved = db.query(models.Skill).filter(models.Skill.status == "approved").count()
    rejected = db.query(models.Skill).filter(models.Skill.status == "rejected").count()
    total_users = db.query(models.User).count()
    return templates.TemplateResponse("admin/panel.html", {
        "request": request,
        "current_user": current_user,
        "pending_skills": pending,
        "approved_count": approved,
        "rejected_count": rejected,
        "total_users": total_users,
        "active_tab": "skills",
    })


# ── Skill approval ───────────────────────────────────────────────────────────

@router.post("/skills/{skill_id}/approve")
def approve_skill(skill_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if skill:
        skill.status = "approved"
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)


@router.post("/skills/{skill_id}/reject")
def reject_skill(skill_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if skill:
        skill.status = "rejected"
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)


# ── User management ──────────────────────────────────────────────────────────

@router.get("/users", response_class=HTMLResponse)
def admin_users(request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    user_data = []
    for u in users:
        skill_count = db.query(models.Skill).filter(models.Skill.author_id == u.id).count()
        user_data.append({
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "skill_count": skill_count,
            "has_yubikey": len(u.webauthn_credentials) > 0,
            "yubikey_count": len(u.webauthn_credentials),
        })
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "current_user": current_user,
        "users": user_data,
        "active_tab": "users",
    })


@router.post("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    import asyncio
    async def _inner():
        form = await request.form()
        new_role = form.get("role", "contributor")
        if new_role not in ("admin", "contributor", "viewer"):
            return RedirectResponse(url="/admin/users", status_code=302)
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user and user.id != current_user.id:  # prevent self-demotion
            user.role = new_role
            db.commit()
        return RedirectResponse(url="/admin/users", status_code=302)
    return asyncio.get_event_loop().run_until_complete(_inner())


@router.post("/users/{user_id}/suspend")
def toggle_suspend(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and user.id != current_user.id:
        user.is_active = not user.is_active
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and user.id != current_user.id:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/create")
async def create_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))
    role = str(form.get("role", "contributor"))

    if not email or not username or not password:
        return RedirectResponse(url="/admin/users?error=missing_fields", status_code=302)
    if db.query(models.User).filter(models.User.email == email).first():
        return RedirectResponse(url="/admin/users?error=email_exists", status_code=302)

    user = models.User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        role=role if role in ("admin", "contributor", "viewer") else "contributor",
    )
    db.add(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)
