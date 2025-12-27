import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

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

# --- Resumo ---
st.header("Resumo do Mês")
resumo = get_resumo(st.session_state["token"])

components.html(
    open("components/cards_component.html").read()
    .replace("{{ item.title }}", "Saldo Total")
    .replace("{{ item.value }}", f"R$ {resumo['saldo_restante']:.2f}"),
    height=120
)

# --- Gráfico ---
df = pd.DataFrame(resumo["detalhes"])
fig = px.bar(df, x="Categoria", y="Valor", color="Tipo")
st.plotly_chart(fig, use_container_width=True)

# --- CSV Fallback ---
st.header("Importar CSV do Notion")
csv = st.file_uploader("Selecione um arquivo CSV", type="csv")
if csv:
    df_csv = pd.read_csv(csv)
    st.write(df_csv.head())
