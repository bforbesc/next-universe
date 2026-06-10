import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{REPO_ROOT / 'backend' / 'nextuniverse.db'}")
CURRICULUM_DIR = Path(os.environ.get("CURRICULUM_DIR", REPO_ROOT / "curriculum"))

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# Comma-separated list of allowed CORS origins for the frontend dev server.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
