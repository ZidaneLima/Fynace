from fastapi import APIRouter, Depends
from backend.auth_utils import verify_jwt

router = APIRouter()

@router.post("/")
def criar_transacao(data: dict, user=Depends(verify_jwt)):
    return {
        "message": "Transação salva",
        "user_id": user["user_id"],
        "email": user["email"]
    }
