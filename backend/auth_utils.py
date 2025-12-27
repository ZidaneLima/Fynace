from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests

security = HTTPBearer()

SUPABASE_PROJECT_REF = "jzdikonmvsxtlheskhjl"
JWKS_URL = f"https://{SUPABASE_PROJECT_REF}.supabase.co/auth/v1/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = next(k for k in jwks["keys"] if k["kid"] == kid)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"https://{SUPABASE_PROJECT_REF}.supabase.co/auth/v1"
        )
        return payload

    except (JWTError, StopIteration):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
