import os
from pathlib import Path
from dotenv import load_dotenv

# === Carrega variáveis de ambiente ===
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".." / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


# === Configurações principais ===
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fynace.db")

GOOGLE_CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS", "client_secret.json")

FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
SECRET_KEY = os.getenv("SECRET_KEY", "DE5SWfLh5f7EilWy_sGzqqQRrE_of5R-4Vs3UPkOgwURDBJRJMT2350O_FoOvDLxGaDSNh2zMjuTaLLvFdDWsA")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")