from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from backend.config import SECRET_KEY, JWT_ALGORITHM
from backend.db import get_db, get_user_by_email

def verify_jwt(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorização ausente ou inválido")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token JWT inválido ou expirado")

    # o payload deve conter o email (conforme gerado no auth)
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="JWT sem email")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Retorna dados necessários para as rotas (token_data = google_token do DB)
    return {
        "email": user.email,
        "spreadsheet_id": user.spreadsheet_id,
        "token_data": user.google_token
    }
