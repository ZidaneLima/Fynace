import os
import subprocess
import time
from dotenv import load_dotenv
from pathlib import Path

# === 1️⃣ Carrega variáveis de ambiente ===
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

if env_path.exists():
    load_dotenv(env_path)
else:
    print("⚠️  .env não encontrado. Certifique-se de criar antes de rodar o projeto.")

# === 2️⃣ Configurações do Backend ===
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./fynace.db")

# === 3️⃣ Checa se o banco existe ===
db_file = BASE_DIR / "fynace.db"
if db_file.exists():
    print("✅ Banco de dados encontrado:", db_file)
else:
    print("🛠️  Criando banco de dados inicial...")
    from backend.db import Base, engine
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados criado com sucesso.")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Permite OAuth2 em HTTP para desenvolvimento

# === 4️⃣ Inicia os serviços ===
print("\n🚀 Iniciando backend (FastAPI)...")
backend_process = subprocess.Popen(
    ["uvicorn", "backend.main:app", "--host", FASTAPI_HOST, "--port", FASTAPI_PORT]
)

time.sleep(3)  # espera o backend subir antes do front

print("🎨 Iniciando frontend (Streamlit)...")
frontend_process = subprocess.Popen(
    ["streamlit", "run", "frontend/app.py"], env=os.environ
)

# === 5️⃣ Mantém o processo vivo até interrupção manual ===
try:
    backend_process.wait()
    frontend_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Encerrando processos...")
    backend_process.terminate()
    frontend_process.terminate()
    print("✅ Projeto finalizado com sucesso.")
