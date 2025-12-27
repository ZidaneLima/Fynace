from fastapi import APIRouter, Depends
from backend.auth_utils import get_current_user

router = APIRouter()

@router.get("/")
def get_resumo(user=Depends(get_current_user)):
    return {
        "total_ganhos": 0,
        "total_despesas": 0,
        "saldo": 0,
        "user": user["email"]
    }
