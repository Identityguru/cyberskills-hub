import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="contributor")  # admin | contributor | viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    skills = relationship("Skill", back_populates="author")
    downloads = relationship("Download", back_populates="user")
    webauthn_credentials = relationship("WebAuthnCredential", back_populates="user", cascade="all, delete-orphan")


class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credential_id = Column(String, unique=True, nullable=False, index=True)  # base64url-encoded
    public_key = Column(LargeBinary, nullable=False)                          # CBOR-encoded public key
    sign_count = Column(Integer, default=0)
    device_name = Column(String, default="YubiKey")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="webauthn_credentials")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, default="")
    vendor = Column(String, default="community")  # okta | sailpoint | cyberark | community
    _tags = Column("tags", Text, default="[]")
    _mitre_attack_ids = Column("mitre_attack_ids", Text, default="[]")
    version = Column(String, default="1.0")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    download_count = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending | approved | rejected
    file_path = Column(String, default="")
    readme_content = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="skills")
    downloads = relationship("Download", back_populates="skill")

    @property
    def tags(self):
        return json.loads(self._tags or "[]")

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)

    @property
    def mitre_attack_ids(self):
        return json.loads(self._mitre_attack_ids or "[]")

    @mitre_attack_ids.setter
    def mitre_attack_ids(self, value):
        self._mitre_attack_ids = json.dumps(value)


class Download(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_hash = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill", back_populates="downloads")
    user = relationship("User", back_populates="downloads")
