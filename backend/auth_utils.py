from fastapi import Header, HTTPException
from jose import jwt, JWTError
import os

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWT_ALG = "HS256"

def verify_jwt(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=[JWT_ALG],
            audience="authenticated",
        )

        return {
            "user_id": payload["sub"],
            "email": payload.get("email")
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="JWT inválido")
