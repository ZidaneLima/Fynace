import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends

from backend.routes import transacoes, resumo
from backend.auth_utils import get_current_user


app = FastAPI(title=os.getenv("APP_NAME", "Fynace"))

app.include_router(transacoes.router, prefix="/transacoes", tags=["Transações"])
app.include_router(resumo.router, prefix="/resumo", tags=["Resumo"])

@app.get("/saudez")
def health():
    return {"status": "ok"}

@app.get("/me")
def me(user=Depends(get_current_user)):
    return user
