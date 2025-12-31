import os


def get_env_or_raise(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente {name} não configurada")
    return value


SUPABASE_URL = get_env_or_raise("SUPABASE_URL")
SUPABASE_ANON_KEY = get_env_or_raise("SUPABASE_ANON_KEY")
SUPABASE_JWT_SECRET = get_env_or_raise("SUPABASE_JWT_SECRET")

# Mercado Pago token
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")  #Not required for core functionality
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")