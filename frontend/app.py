import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import requests
import os

from utils.api_client import get_resumo, post_transacao

st.set_page_config(page_title="Fynace", layout="wide")

# --- Captura token da URL ---
query_params = st.query_params
token = query_params.get("token", [None])[0] if "token" in query_params else None
email = query_params.get("email", [None])[0] if "email" in query_params else None

if token:
    st.session_state["token"] = token
if email:
    st.session_state["user_email"] = email

# --- Logout ---
def logout():
    for key in ["user_email", "token"]:
        st.session_state.pop(key, None)
    st.success("Logout realizado com sucesso.")

# --- Se não logado ---
if "token" not in st.session_state:
    st.title("Fynace")
    st.info("Você precisa estar autenticado para acessar o sistema.")
    st.markdown(
        """
        🔐 Faça login pelo Supabase e volte com o token na URL
        Exemplo:
        ```
        http://localhost:8501/?token=SEU_JWT&email=seu@email.com
        ```
        """
    )
    st.stop()

# --- Logado ---
st.sidebar.success(f"🔹 Logado como: {st.session_state.get('user_email', 'Usuário')}")
st.sidebar.button("Logout", on_click=logout)

st.title("📊 Fynace - Dashboard Financeiro")

# --- Status do Usuário ---
st.sidebar.header("Status do Usuário")
st.sidebar.info(f"Usuário: {st.session_state.get('user_email', 'Desconhecido')}")

# --- Adicionar Transação ---
st.sidebar.header("Adicionar Transação")
descricao = st.sidebar.text_input("Descrição")
valor = st.sidebar.number_input("Valor", min_value=0.0, format="%.2f")
tipo = st.sidebar.radio("Tipo", ["Despesa", "Ganho"])
categoria = st.sidebar.selectbox(
    "Categoria",
    ["Alimentação", "Transporte", "Lazer", "Saúde", "Investimentos", "Outros"]
    if tipo == "Despesa"
    else ["Salário", "Freelancer", "Outros"]
)

if st.sidebar.button("Adicionar"):
    try:
        post_transacao(
            {
                "descricao": descricao,
                "valor": valor,
                "tipo": tipo.lower(),
                "categoria": categoria
            },
            st.session_state["token"]
        )
        st.success("Transação adicionada com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao adicionar transação: {str(e)}")

# --- Resumo ---
st.header("Resumo do Mês")
try:
    resumo = get_resumo(st.session_state["token"])

    # Create a simple card component using HTML
    card_html = f"""
    <div class="card">
      <h3>Saldo Total</h3>
      <p>R$ {resumo['saldo']:.2f}</p>
    </div>

    <style>
    .card {{
      background: linear-gradient(135deg, #3a7bd5, #3a6073);
      color: white;
      padding: 1.2rem 1.5rem;
      border-radius: 16px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.1);
      min-width: 200px;
      text-align: center;
      margin: 0 auto;
      max-width: 300px;
    }}
    .card h3 {{
      margin: 0;
      font-size: 1rem;
      opacity: 0.9;
    }}
    .card p {{
      font-size: 1.3rem;
      font-weight: bold;
      margin: 0.4rem 0 0;
    }}
    </style>
    """

    components.html(card_html, height=120)

    # --- Gráfico ---
    df = pd.DataFrame(resumo["detalhes"])
    if not df.empty:
        fig = px.bar(df, x="Categoria", y="Valor", color="Tipo")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma transação registrada ainda.")
except Exception as e:
    st.error(f"Erro ao carregar resumo: {str(e)}")

# --- Visualização de Transações ---
st.header("Transações Recentes")
try:
    api_url = os.getenv("API_URL", "http://127.0.0.1:8000")
    response = requests.get(
        f"{api_url}/transacoes",
        headers={
            "Authorization": f"Bearer {st.session_state['token']}",
            "Content-Type": "application/json"
        }
    )
    if response.status_code == 200:
        transacoes_data = response.json()
        transacoes = transacoes_data.get("transactions", [])

        if transacoes:
            df_transacoes = pd.DataFrame(transacoes)
            st.dataframe(df_transacoes, use_container_width=True)
        else:
            st.info("Nenhuma transação registrada ainda.")
    else:
        st.error("Erro ao carregar transações")
except Exception as e:
    st.error(f"Erro ao carregar transações: {str(e)}")

# --- CSV Fallback ---
st.header("Importar CSV do Notion")
csv = st.file_uploader("Selecione um arquivo CSV", type="csv")
if csv:
    df_csv = pd.read_csv(csv)
    st.write(df_csv.head())
