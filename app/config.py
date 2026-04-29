from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    partial_token_expire_minutes: int = 5  # FIDO2 pending window
    database_url: str = f"sqlite:///{BASE_DIR}/cyberskills.db"
    skills_data_dir: str = str(BASE_DIR / "skills_data")
    admin_email: str = "raj@cloudidentityhub.com"
    admin_password: str = "model2Skills2026"
    admin_username: str = "identityguru"
    rp_id: str = "localhost"
    rp_name: str = "CyberSkills Hub"
    origin: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
