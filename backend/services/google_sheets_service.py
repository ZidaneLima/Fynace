"""Google Sheets service for Fynace application using service account."""
import logging
import os
from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from backend.models.transaction import TransactionCreate, TransactionType

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class GoogleSheetsService:
    def __init__(self):
        """Initialize the Google Sheets service with service account credentials."""
        # Get service account file path from environment
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if not service_account_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable not set")

        # Load credentials from service account file
        credentials = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        self.service = build("sheets", "v4", credentials=credentials)

    def create_user_spreadsheet(self, user_email: str) -> str:
        """Create a new spreadsheet for the user and return the ID."""
        title = f"Fynace - Finanças de {user_email.split('@')[0]}"
        sheet = self.service.spreadsheets().create(
            body={"properties": {"title": title}},
            fields="spreadsheetId"
        ).execute()
        spreadsheet_id = sheet.get("spreadsheetId")

        # Create sheets
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {"addSheet": {"properties": {"title": "Despesas"}}},
                    {"addSheet": {"properties": {"title": "Ganhos"}}},
                    {"addSheet": {"properties": {"title": "Resumo"}}},
                ]
            }
        ).execute()

        # Add basic headers
        for sheet_name in ["Despesas", "Ganhos"]:
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:E1",
                valueInputOption="RAW",
                body={"values": [["Data", "Descrição", "Categoria", "Valor", "Tipo"]]}
            ).execute()

        logger.info(f"Spreadsheet created with ID: {spreadsheet_id}")
        return spreadsheet_id

    def append_transaction(self, spreadsheet_id: str, transaction: TransactionCreate) -> bool:
        """Append a new transaction to the appropriate sheet."""
        try:
            sheet_name = "Despesas" if transaction.tipo == TransactionType.expense else "Ganhos"
            values = [
                transaction.data.isoformat() if transaction.data else datetime.now().isoformat(),
                transaction.descricao,
                transaction.categoria,
                transaction.valor,
                transaction.tipo.value.capitalize()
            ]

            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:E",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [values]}
            ).execute()

            logger.info(f"Transaction saved to {sheet_name} sheet.")
            return True
        except HttpError as e:
            logger.error(f"Error inserting transaction: {e}")
            return False

    def read_transactions(self, spreadsheet_id: str, sheet_name: str, range_: str = "A2:E") -> List[List[Any]]:
        """Read transactions from a specific sheet."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!{range_}"
            ).execute()
            return result.get("values", [])
        except HttpError as e:
            logger.error(f"Error reading transactions: {e}")
            return []

    def get_summary(self, spreadsheet_id: str) -> Dict[str, float]:
        """Calculate financial summary from the spreadsheet."""
        expenses = self.read_transactions(spreadsheet_id, "Despesas")
        incomes = self.read_transactions(spreadsheet_id, "Ganhos")

        total_expenses = sum(float(row[3]) for row in expenses if len(row) > 3 and row[3].replace('.', '', 1).isdigit())
        total_incomes = sum(float(row[3]) for row in incomes if len(row) > 3 and row[3].replace('.', '', 1).isdigit())

        return {
            "total_ganhos": total_incomes,
            "total_despesas": total_expenses,
            "saldo": total_incomes - total_expenses
        }

    def get_category_breakdown(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Get category breakdown for visualization."""
        expenses = self.read_transactions(spreadsheet_id, "Despesas")
        incomes = self.read_transactions(spreadsheet_id, "Ganhos")

        categories = {}

        # Process expenses
        for row in expenses:
            if len(row) >= 4:
                category = row[2] if len(row) > 2 else "Outros"
                amount = float(row[3]) if row[3].replace('.', '', 1).isdigit() else 0
                if category not in categories:
                    categories[category] = {"Despesa": 0, "Ganho": 0}
                categories[category]["Despesa"] += amount

        # Process incomes
        for row in incomes:
            if len(row) >= 4:
                category = row[2] if len(row) > 2 else "Outros"
                amount = float(row[3]) if row[3].replace('.', '', 1).isdigit() else 0
                if category not in categories:
                    categories[category] = {"Despesa": 0, "Ganho": 0}
                categories[category]["Ganho"] += amount

        result = []
        for category, amounts in categories.items():
            for trans_type, amount in amounts.items():
                if amount > 0:
                    result.append({
                        "Categoria": category,
                        "Tipo": trans_type,
                        "Valor": amount
                    })

        return result