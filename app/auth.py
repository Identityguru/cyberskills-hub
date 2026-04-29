import time
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# In-memory challenge store: {user_id: (challenge_bytes, expires_at)}
_challenge_store: dict[int, tuple[bytes, float]] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire, "type": "full"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_partial_token(user_id: int) -> str:
    """Short-lived token issued after password check, before FIDO2 verification."""
    expire = datetime.utcnow() + timedelta(minutes=settings.partial_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "partial"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_partial_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "partial":
            return None
        return int(payload.get("sub"))
    except JWTError:
        return None


def store_webauthn_challenge(user_id: int, challenge: bytes, ttl_seconds: int = 300) -> None:
    _challenge_store[user_id] = (challenge, time.time() + ttl_seconds)


def pop_webauthn_challenge(user_id: int) -> Optional[bytes]:
    entry = _challenge_store.pop(user_id, None)
    if entry is None:
        return None
    challenge, expires_at = entry
    if time.time() > expires_at:
        return None
    return challenge


def _token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return request.cookies.get("access_token")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    token = _token_from_request(request)
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "full":
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user and not user.is_active:
        return None
    return user


def require_auth(current_user: Optional[models.User] = Depends(get_current_user)) -> models.User:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return current_user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
