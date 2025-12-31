import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def _headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_resumo(token: str):
    response = requests.get(
        f"{BACKEND_URL}/resumo",
        headers=_headers(token)
    )
    response.raise_for_status()
    return response.json()


def post_transacao(data: dict, token: str):
    response = requests.post(
        f"{BACKEND_URL}/transacoes",
        json=data,
        headers=_headers(token)
    )
    response.raise_for_status()
    return response.json()
