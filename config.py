import os
from dotenv import load_dotenv

load_dotenv()


_ROOT = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "aseel-capstone-dev-secret-key")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@aseel.ae")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AseelAdmin2026!")
    DATABASE_PATH = os.getenv("DATABASE_PATH") or os.path.join(_ROOT, "aseel.db")
    QR_FOLDER = os.getenv("QR_FOLDER") or os.path.join(_ROOT, "static", "qr")
    BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
    DEFAULT_SCAN_THRESHOLD = 5
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = BASE_URL.startswith("https")
