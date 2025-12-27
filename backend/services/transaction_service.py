"""Transaction processing service for Fynace application."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.services.google_sheets_service import GoogleSheetsService
from backend.models.transaction import TransactionCreate, Transaction, TransactionType
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        # Initialize Google Sheets service with service account credentials
        self.sheets_service = GoogleSheetsService()

    def create_transaction(self, transaction: TransactionCreate) -> bool:
        """Create a new transaction in Google Sheets."""
        try:
            # Set the transaction date if not provided
            if not transaction.data:
                transaction.data = datetime.now()

            # Validate transaction data
            if not self._validate_transaction(transaction):
                return False

            # Save to Google Sheets
            success = self.sheets_service.append_transaction(self.spreadsheet_id, transaction)

            if success:
                logger.info(f"Transaction created successfully: {transaction.descricao}")
            else:
                logger.error(f"Failed to create transaction: {transaction.descricao}")

            return success
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return False

    def _validate_transaction(self, transaction: TransactionCreate) -> bool:
        """Validate transaction data before processing."""
        # Check required fields
        if not transaction.descricao or not transaction.descricao.strip():
            logger.error("Transaction description is required")
            return False

        if transaction.valor <= 0:
            logger.error("Transaction value must be positive")
            return False

        if transaction.tipo not in [TransactionType.expense, TransactionType.income]:
            logger.error(f"Invalid transaction type: {transaction.tipo}")
            return False

        if not transaction.categoria or not transaction.categoria.strip():
            logger.error("Transaction category is required")
            return False

        return True

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions from both expense and income sheets."""
        try:
            expenses = self.sheets_service.read_transactions(self.spreadsheet_id, "Despesas")
            incomes = self.sheets_service.read_transactions(self.spreadsheet_id, "Ganhos")

            transactions = []

            # Process expenses
            for row in expenses:
                if len(row) >= 5:  # Ensure we have all required fields
                    transactions.append({
                        "data": row[0] if row[0] else "",
                        "descricao": row[1] if row[1] else "",
                        "categoria": row[2] if row[2] else "",
                        "valor": float(row[3]) if row[3] and row[3].replace('.', '', 1).isdigit() else 0,
                        "tipo": "despesa"
                    })

            # Process incomes
            for row in incomes:
                if len(row) >= 5:  # Ensure we have all required fields
                    transactions.append({
                        "data": row[0] if row[0] else "",
                        "descricao": row[1] if row[1] else "",
                        "categoria": row[2] if row[2] else "",
                        "valor": float(row[3]) if row[3] and row[3].replace('.', '', 1).isdigit() else 0,
                        "tipo": "ganho"
                    })

            return transactions
        except Exception as e:
            logger.error(f"Error getting all transactions: {e}")
            return []

    def get_transactions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get transactions filtered by category."""
        all_transactions = self.get_all_transactions()
        return [t for t in all_transactions if t["categoria"].lower() == category.lower()]

    def get_transactions_by_type(self, trans_type: TransactionType) -> List[Dict[str, Any]]:
        """Get transactions filtered by type (expense or income)."""
        all_transactions = self.get_all_transactions()
        return [t for t in all_transactions if t["tipo"] == trans_type.value]

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get transactions within a specific date range."""
        all_transactions = self.get_all_transactions()
        filtered_transactions = []

        for transaction in all_transactions:
            try:
                # Parse the date string from Google Sheets
                if transaction["data"]:
                    # Google Sheets date format might vary, try different formats
                    trans_date = self._parse_date(transaction["data"])
                    if trans_date and start_date <= trans_date <= end_date:
                        filtered_transactions.append(transaction)
            except Exception:
                # If date parsing fails, skip this transaction
                continue

        return filtered_transactions

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from Google Sheets."""
        try:
            # Google Sheets typically returns dates in ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try parsing as a different format if ISO fails
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # If all parsing fails, return None
                return None