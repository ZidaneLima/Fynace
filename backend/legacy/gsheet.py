from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
import logging



logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_service(token_data: dict):
    """Cria o serviço autenticado do Sheets API.""" 
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    return build("sheets", "v4", credentials=creds)


def create_user_sheet(service, title: str) -> str:
    """Cria uma nova planilha para o usuário e retorna o ID."""
    sheet = service.spreadsheets().create(
        body={"properties": {"title": title}},
        fields="spreadsheetId"
    ).execute()
    spreadsheet_id = sheet.get("spreadsheetId")

    # Cria abas
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {"addSheet": {"properties": {"title": "Despesas"}}},
                {"addSheet": {"properties": {"title": "Ganhos"}}},
                {"addSheet": {"properties": {"title": "Resumo"}}},
            ]
        }
    ).execute()

    # Cabeçalhos básicos
    for aba in ["Despesas", "Ganhos"]:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{aba}!A1:E1",
            valueInputOption="RAW",
            body={"values": [["Data", "Descrição", "Categoria", "Valor", "Tipo"]]}
        ).execute()

    logger.info(f"Planilha criada com ID: {spreadsheet_id}")
    return spreadsheet_id


def append_row(service, spreadsheet_id: str, sheet_name: str, values: List):
    """Adiciona uma nova linha na aba especificada."""
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:E",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [values]}
        ).execute()
    except HttpError as e:
        logger.error(f"Erro ao inserir linha: {e}")
        raise


def read_range(service, spreadsheet_id: str, sheet_name: str, range_: str = "A:E"):
    """Lê um intervalo de dados de uma aba."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!{range_}"
        ).execute()
        return result.get("values", [])
    except HttpError as e:
        logger.error(f"Erro ao ler range: {e}")
        raise

def salvar_no_google_sheets(service, spreadsheet_id: str, email: str, transacao: dict):
    """Insere uma nova transação na planilha do usuário."""
    try:
        sheet_name = "Despesas" if transacao["tipo"].lower() == "despesa" else "Ganhos"
        values = [
            transacao.get("data"),
            transacao.get("descricao"),
            transacao.get("categoria"),
            transacao.get("valor"),
            transacao.get("tipo").capitalize() # type: ignore
        ]
        append_row(service, spreadsheet_id, sheet_name, values)
        logger.info(f"Transação salva na aba {sheet_name} para {email}.")
    except Exception as e:
        logger.error(f"Erro ao salvar no Google Sheets: {e}")
        raise