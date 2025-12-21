from fastapi import APIRouter, Depends, HTTPException
from backend.db import get_db
from backend.models import User
from backend.gsheet import get_service, append_row
import datetime

router = APIRouter(prefix="/transacoes", tags=["Transações"])

@router.post("/")
def add_transacao(
    email: str,  # Depois precisa altera para validar pelo token do user
    descricao: str,
    valor: float,
    tipo: str,
    categoria: str = None, # type: ignore
    db=Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not user.spreadsheet_id:
        raise HTTPException(status_code=400, detail="Planilha não vinculada")

    # Obter credenciais (depois vamos descriptografar o refresh_token)
    token_data = {"token": user.refresh_token_encrypted}  #  substituir por decrypt
    service = get_service(token_data)

    sheet_name = "Despesas" if tipo.lower() == "despesa" else "Ganhos"
    data = datetime.date.today().isoformat()
    values = [data, descricao, categoria or "-", valor, tipo.capitalize()]

    append_row(service, user.spreadsheet_id, sheet_name, values)

    return {"message": "Transação adicionada com sucesso!"}
