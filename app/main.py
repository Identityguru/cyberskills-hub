from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.database import engine, Base
from app.routers import skills, auth, admin, webauthn

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CyberSkills Hub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(skills.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(webauthn.router)
