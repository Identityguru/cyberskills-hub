from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class SkillOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    category: str
    subcategory: str
    vendor: str
    tags: List[str]
    mitre_attack_ids: List[str]
    version: str
    download_count: int
    status: str
    readme_content: str
    created_at: datetime
    author_username: Optional[str] = None

    class Config:
        from_attributes = True


class SkillStatusUpdate(BaseModel):
    status: str  # approved | rejected
