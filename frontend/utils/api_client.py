import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

def login_with_google():
    try:
        response = requests.get(f"{API_URL}/auth/google/login")
        response.raise_for_status()
        auth_url = response.json().get("auth_url")

        if auth_url:
            st.markdown(f"[🔐 Entrar com Google]({auth_url})")
        else:
            st.error("Não foi possível obter a URL de autenticação.")
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")


def get_resumo(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/resumo/", headers=headers).json()

def post_transacao(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/transacoes/", params=data, headers=headers)
    