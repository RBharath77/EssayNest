from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models"
ARTIFACT_DIR = ROOT / "training" / "artifacts"
DB_PATH = ROOT / "backend" / "essay_scorer.db"
REPORT_DIR = ROOT / "reports" / "generated"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 24
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
RESET_TOKEN_MINUTES = int(os.getenv("RESET_TOKEN_MINUTES", "30"))
FRONTEND_ORIGINS = [
    x.strip() for x in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",") if x.strip()
]
