from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import (
    hash_password, verify_password, create_access_token,
    create_partial_token, get_current_user,
)
from pathlib import Path

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("auth/register.html", {"request": request, "current_user": current_user})


@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))

    if db.query(models.User).filter(models.User.email == email).first():
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "error": "Email already registered.", "current_user": None
        })
    if db.query(models.User).filter(models.User.username == username).first():
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "error": "Username already taken.", "current_user": None
        })
    user = models.User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        role="contributor",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=86400 * 7)
    return response


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("auth/login.html", {"request": request, "current_user": current_user})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {
            "request": request, "error": "Invalid email or password.", "current_user": None
        })
    if not user.is_active:
        return templates.TemplateResponse("auth/login.html", {
            "request": request, "error": "Account suspended. Contact administrator.", "current_user": None
        })

    # Admin users with a registered YubiKey → require FIDO2 second factor
    if user.role == "admin" and user.webauthn_credentials:
        partial = create_partial_token(user.id)
        response = RedirectResponse(url="/auth/fido2/challenge", status_code=302)
        response.set_cookie("partial_token", partial, httponly=True, max_age=300, samesite="lax")
        return response

    # Admin without a key → full login with warning
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/admin" if user.role == "admin" else "/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=86400 * 7)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("partial_token")
    return response
