from backend.routes import transacoes, resumo
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from backend.auth import router as auth_router


load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME", "Fynace API"))
app.include_router(auth_router)

app.include_router(transacoes.router, prefix="/transacoes", tags=["Transações"])
app.include_router(resumo.router, prefix="/resumo", tags=["Resumo"])
