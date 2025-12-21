from fastapi import APIRouter, Depends, HTTPException
from backend.db import get_db
from backend.models import User
from backend.gsheet import get_service, read_range

router = APIRouter(prefix="/resumo", tags=["Resumo"])

@router.get("/")
def get_resumo(email: str, db=Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.spreadsheet_id:
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou sem planilha")

    token_data = {"token": user.refresh_token_encrypted}  #  substituir depois
    service = get_service(token_data)

    ganhos = read_range(service, user.spreadsheet_id, "Ganhos")
    despesas = read_range(service, user.spreadsheet_id, "Despesas")

    total_ganhos = sum(float(x[3]) for x in ganhos[1:] if len(x) > 3)
    total_despesas = sum(float(x[3]) for x in despesas[1:] if len(x) > 3)
    saldo = total_ganhos - total_despesas

    return {
        "total_ganhos": total_ganhos,
        "total_despesas": total_despesas,
        "saldo": saldo
    }
