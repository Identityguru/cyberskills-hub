"""
FIDO2 / WebAuthn registration and authentication for admin MFA.

Flow:
  Registration (admin-only):
    GET  /auth/fido2/register          → page
    POST /auth/fido2/register/begin    → returns JSON options
    POST /auth/fido2/register/complete → verifies + stores credential

  Authentication (called after password check for admin users):
    POST /auth/fido2/authenticate/begin    → returns JSON options
    POST /auth/fido2/authenticate/complete → verifies assertion, issues full token
"""
import base64
import json
from datetime import datetime

import webauthn
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app import models
from app.auth import (
    create_access_token,
    decode_partial_token,
    get_current_user,
    pop_webauthn_challenge,
    require_admin,
    store_webauthn_challenge,
)
from app.config import settings
from app.database import get_db
from pathlib import Path

router = APIRouter(prefix="/auth/fido2", tags=["fido2"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


# ── Registration ────────────────────────────────────────────────────────────

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, current_user=Depends(require_admin)):
    existing = current_user.webauthn_credentials
    return templates.TemplateResponse("auth/fido2_register.html", {
        "request": request,
        "current_user": current_user,
        "existing_keys": existing,
    })


@router.post("/register/begin")
def registration_begin(request: Request, current_user: models.User = Depends(require_admin)):
    options = webauthn.generate_registration_options(
        rp_id=settings.rp_id,
        rp_name=settings.rp_name,
        user_id=str(current_user.id).encode(),
        user_name=current_user.email,
        user_display_name=current_user.username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.DISCOURAGED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=[
            webauthn.helpers.structs.PublicKeyCredentialDescriptor(
                id=base64url_to_bytes(cred.credential_id)
            )
            for cred in current_user.webauthn_credentials
        ],
    )
    store_webauthn_challenge(current_user.id, options.challenge)
    return JSONResponse(json.loads(webauthn.options_to_json(options)))


@router.post("/register/complete")
async def registration_complete(
    request: Request,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    body = await request.json()
    device_name = body.pop("device_name", "YubiKey")
    challenge = pop_webauthn_challenge(current_user.id)
    if not challenge:
        raise HTTPException(status_code=400, detail="Challenge expired or not found. Try again.")

    try:
        verified = webauthn.verify_registration_response(
            credential=body,
            expected_challenge=challenge,
            expected_rp_id=settings.rp_id,
            expected_origin=settings.origin,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Registration failed: {exc}")

    cred = models.WebAuthnCredential(
        user_id=current_user.id,
        credential_id=bytes_to_base64url(verified.credential_id),
        public_key=verified.credential_public_key,
        sign_count=verified.sign_count,
        device_name=device_name,
    )
    db.add(cred)
    db.commit()
    return JSONResponse({"status": "ok", "device_name": device_name})


@router.post("/credentials/{cred_id}/delete")
def delete_credential(
    cred_id: int,
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cred = db.query(models.WebAuthnCredential).filter(
        models.WebAuthnCredential.id == cred_id,
        models.WebAuthnCredential.user_id == current_user.id,
    ).first()
    if cred:
        db.delete(cred)
        db.commit()
    return RedirectResponse(url="/auth/fido2/register", status_code=302)


# ── Authentication ───────────────────────────────────────────────────────────

@router.get("/challenge", response_class=HTMLResponse)
def fido2_challenge_page(request: Request, db: Session = Depends(get_db)):
    """Shown after password auth for admin users who have a registered key."""
    partial_token = request.cookies.get("partial_token")
    user_id = decode_partial_token(partial_token or "")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=302)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != "admin":
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse("auth/fido2_challenge.html", {
        "request": request,
        "current_user": None,
        "username": user.username,
    })


@router.post("/authenticate/begin")
def authentication_begin(request: Request, db: Session = Depends(get_db)):
    partial_token = request.cookies.get("partial_token")
    user_id = decode_partial_token(partial_token or "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only.")

    creds = user.webauthn_credentials
    if not creds:
        raise HTTPException(status_code=400, detail="No security key registered.")

    options = webauthn.generate_authentication_options(
        rp_id=settings.rp_id,
        allow_credentials=[
            webauthn.helpers.structs.PublicKeyCredentialDescriptor(
                id=base64url_to_bytes(c.credential_id)
            )
            for c in creds
        ],
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    store_webauthn_challenge(user.id, options.challenge)
    return JSONResponse(json.loads(webauthn.options_to_json(options)))


@router.post("/authenticate/complete")
async def authentication_complete(request: Request, db: Session = Depends(get_db)):
    partial_token = request.cookies.get("partial_token")
    user_id = decode_partial_token(partial_token or "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired.")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403)

    challenge = pop_webauthn_challenge(user.id)
    if not challenge:
        raise HTTPException(status_code=400, detail="Challenge expired. Please try again.")

    body = await request.json()
    raw_id = body.get("rawId") or body.get("id")
    cred_id_b64 = raw_id if isinstance(raw_id, str) else bytes_to_base64url(base64.b64decode(raw_id))

    db_cred = db.query(models.WebAuthnCredential).filter(
        models.WebAuthnCredential.credential_id == cred_id_b64,
        models.WebAuthnCredential.user_id == user.id,
    ).first()
    if not db_cred:
        raise HTTPException(status_code=400, detail="Unknown credential.")

    try:
        verified = webauthn.verify_authentication_response(
            credential=body,
            expected_challenge=challenge,
            expected_rp_id=settings.rp_id,
            expected_origin=settings.origin,
            credential_public_key=db_cred.public_key,
            credential_current_sign_count=db_cred.sign_count,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {exc}")

    db_cred.sign_count = verified.new_sign_count
    db_cred.last_used_at = datetime.utcnow()
    db.commit()

    full_token = create_access_token({"sub": str(user.id)})
    response = JSONResponse({"status": "ok", "redirect": "/"})
    response.set_cookie("access_token", full_token, httponly=True, max_age=86400 * 7)
    response.delete_cookie("partial_token")
    return response
