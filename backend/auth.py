from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from backend.gsheet import create_user_sheet, get_service
from datetime import datetime, timedelta
from backend.db import SessionLocal
from backend.models import User
from backend.config import GOOGLE_CLIENT_SECRETS_FILE, BACKEND_URL, FRONTEND_URL, SECRET_KEY, JWT_ALGORITHM
from jose import jwt

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google/login")
def google_login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/spreadsheets",
            "openid",
        ],
        redirect_uri=f"{BACKEND_URL}/auth/google/callback",
    )
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return {"auth_url": auth_url}

@router.get("/google/callback")
def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Código ausente") 

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/spreadsheets",
            "openid",
        ],
        redirect_uri=f"{BACKEND_URL}/auth/google/callback",
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Pega info do usuário
    token_request = requests.Request()
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, token_request, flow.client_config["client_id"] # type: ignore
    )
    email = id_info.get("email")

    db = SessionLocal()

    # Verifica se já existe usuário
    user = db.query(User).filter(User.email == email).first()
    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": getattr(credentials, "token_uri", None),
        "client_id": getattr(credentials, "client_id", None),
        "client_secret": getattr(credentials, "client_secret", None),
        "scopes": list(getattr(credentials, "scopes", [])),
    }

    if not user:
        # Cria service e planilha individual
        service = get_service(token_data)
        spreadsheet_id = create_user_sheet(service, f"Fynace_{email.split('@')[0]}")

        user = User(
            email=email,
            spreadsheet_id=spreadsheet_id,
            google_token=token_data,
            refresh_token_encrypted=credentials.refresh_token
        )
        db.add(user)
        db.commit()
    else:
        # Atualiza token/planilha caso houve mudança
        user.google_token = token_data
        if not user.spreadsheet_id:
            service = get_service(token_data)
            user.spreadsheet_id = create_user_sheet(service, f"Fynace_{email.split('@')[0]}")
        db.commit()

    # Gera JWT interno (contendo o email)
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=4),
        "iat": datetime.utcnow(),
    }
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

    db.close()

    # Redireciona de volta ao frontend
    redirect_url = f"{FRONTEND_URL}?email={email}&token={jwt_token}"
    return RedirectResponse(url=redirect_url)
