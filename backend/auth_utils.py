from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
import os
from typing import Dict, Any

security = HTTPBearer()

SUPABASE_PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF", "jzdikonmvsxtlheskhjl")
JWKS_URL = f"https://{SUPABASE_PROJECT_REF}.supabase.co/auth/v1/.well-known/jwks.json"

# Fetch JWKS once at startup
try:
    jwks = requests.get(JWKS_URL).json()
except requests.RequestException as e:
    print(f"Error fetching JWKS: {e}")
    jwks = {"keys": []}

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido - kid não encontrado",
            )

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido - chave não encontrada",
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"https://{SUPABASE_PROJECT_REF}.supabase.co/auth/v1"
        )

        # Extract user ID and email from the JWT payload
        # The Supabase handles authentication, we only validate the token
        user_id = payload.get("sub")
        email = payload.get("email")

        # Return basic user information from the JWT
        # Google credentials and spreadsheet ID will be retrieved separately when needed
        user_data = {
            "id": user_id,
            "email": email,
        }

        return user_data

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido - chave não encontrada",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro na validação do token: {str(e)}",
        )
