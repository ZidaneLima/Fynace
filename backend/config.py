import os


def get_env_or_raise(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente {name} não configurada")
    return value


SUPABASE_URL = get_env_or_raise("SUPABASE_URL")
SUPABASE_ANON_KEY = get_env_or_raise("SUPABASE_ANON_KEY")
SUPABASE_ANON_KEY = get_env_or_raise("SUPABASE_JWT_SECRET")

MP_ACCESS_TOKEN = get_env_or_raise("MP_ACCESS_TOKEN")
