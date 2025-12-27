import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv()

FASTAPI_HOST = "127.0.0.1"
FASTAPI_PORT = "8000"

print("🚀 Iniciando backend (FastAPI)...")
backend = subprocess.Popen(
    ["uvicorn", "backend.main:app", "--reload", "--host", FASTAPI_HOST, "--port", FASTAPI_PORT]
)

time.sleep(3)

print("🎨 Iniciando frontend (Streamlit)...")
frontend = subprocess.Popen(
    ["streamlit", "run", "frontend/app.py"],
    env=os.environ
)

try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    print("\n🛑 Encerrando serviços...")
    backend.terminate()
    frontend.terminate()
