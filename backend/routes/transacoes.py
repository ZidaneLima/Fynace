from fastapi import APIRouter, Depends
from backend.auth_utils import get_current_user

router = APIRouter()

@router.post("/")
def criar_transacao(data: dict, user=Depends(get_current_user)):
    return {
        "message": "Transação recebida",
        "user_id": user["id"],
        "email": user["email"],
        "payload": data
    }
