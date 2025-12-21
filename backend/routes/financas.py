from fastapi import APIRouter, Depends
from backend.auth_utils import verify_jwt
from backend.gsheet import get_service, append_row, read_range

router = APIRouter(prefix="/financas", tags=["finanças"])

@router.get("/resumo")
def get_resumo(user=Depends(verify_jwt)):
    service = get_service(user["token_data"])
    data = read_range(service, user["spreadsheet_id"], "Resumo")
    return {"email": user["email"], "resumo": data}


@router.post("/transacoes")
def post_transacao(transacao: dict, user=Depends(verify_jwt)):
    service = get_service(user["token_data"])
    sheet_name = "Ganhos" if transacao["tipo"] == "ganho" else "Despesas"
    
    append_row(
        service,
        user["spreadsheet_id"],
        sheet_name,
        [transacao["data"], transacao["descricao"], transacao["categoria"], transacao["valor"], transacao["tipo"]]
    )
    return {"message": f"Transação salva com sucesso para {user['email']}"}
