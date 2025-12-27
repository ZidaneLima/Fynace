from fastapi import APIRouter, Depends, HTTPException
from backend.auth_utils import get_current_user
from backend.models.transaction import TransactionCreate, TransactionType
from backend.services.transaction_service import TransactionService
from backend.utils.monitoring import monitoring_service
from backend.utils.security import DataValidator, SecurityUtils
from backend.database.database_service import DatabaseService
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
def criar_transacao(transaction: TransactionCreate, user=Depends(get_current_user)):
    try:
        # Validate transaction data
        is_valid, validation_msg = DataValidator.validate_transaction_data(transaction.dict())
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_msg)

        # Initialize database service to get user's spreadsheet ID
        db_service = DatabaseService()

        # Get user's spreadsheet ID from the database
        spreadsheet_id = db_service.get_spreadsheet_id(user["id"])
        if not spreadsheet_id:
            # Create a new spreadsheet if one doesn't exist
            from backend.services.google_sheets_service import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            spreadsheet_id = sheets_service.create_user_spreadsheet(user["email"])

            # Save the spreadsheet ID to the database
            success = db_service.save_spreadsheet_id(user["id"], spreadsheet_id)
            if not success:
                raise HTTPException(status_code=500, detail="Erro ao salvar ID da planilha no banco de dados")

        # Initialize transaction service
        transaction_service = TransactionService(spreadsheet_id)

        # Create transaction using the service
        success = transaction_service.create_transaction(transaction)

        # Log the transaction operation
        monitoring_service.log_transaction_operation(
            user_id=user["id"],
            operation="create_transaction",
            success=success,
            details={
                "transaction_type": transaction.tipo.value,
                "transaction_category": transaction.categoria,
                "transaction_amount": transaction.valor
            }
        )

        if not success:
            raise HTTPException(status_code=500, detail="Erro ao salvar transação no Google Sheets")

        return {
            "message": "Transação criada com sucesso",
            "user_id": user["id"],
            "email": user["email"],
            "transaction": transaction.dict()
        }
    except HTTPException:
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation="create_transaction",
            success=False,
            details={
                "error": "HTTP exception occurred"
            }
        )
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation="create_transaction",
            success=False,
            details={
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao processar criação de transação: {str(e)}")

@router.get("/")
def get_transacoes(user=Depends(get_current_user)):
    """Get all transactions for the user."""
    try:
        # Initialize database service to get user's spreadsheet ID
        db_service = DatabaseService()

        # Get user's spreadsheet ID from the database
        spreadsheet_id = db_service.get_spreadsheet_id(user["id"])
        if not spreadsheet_id:
            # Create a new spreadsheet if one doesn't exist
            from backend.services.google_sheets_service import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            spreadsheet_id = sheets_service.create_user_spreadsheet(user["email"])

            # Save the spreadsheet ID to the database
            success = db_service.save_spreadsheet_id(user["id"], spreadsheet_id)
            if not success:
                raise HTTPException(status_code=500, detail="Erro ao salvar ID da planilha no banco de dados")

        # Initialize transaction service
        transaction_service = TransactionService(spreadsheet_id)

        # Get all transactions
        transactions = transaction_service.get_all_transactions()

        # Log the transaction operation
        monitoring_service.log_transaction_operation(
            user_id=user["id"],
            operation="get_all_transactions",
            success=True,
            details={
                "transaction_count": len(transactions)
            }
        )

        return {
            "transactions": transactions,
            "count": len(transactions),
            "user_id": user["id"]
        }
    except HTTPException:
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation="get_all_transactions",
            success=False,
            details={
                "error": "HTTP exception occurred"
            }
        )
        raise
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation="get_all_transactions",
            success=False,
            details={
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao obter transações: {str(e)}")

@router.get("/categoria/{categoria}")
def get_transacoes_por_categoria(categoria: str, user=Depends(get_current_user)):
    """Get transactions filtered by category."""
    try:
        # Initialize database service to get user's spreadsheet ID
        db_service = DatabaseService()

        # Get user's spreadsheet ID from the database
        spreadsheet_id = db_service.get_spreadsheet_id(user["id"])
        if not spreadsheet_id:
            # Create a new spreadsheet if one doesn't exist
            from backend.services.google_sheets_service import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            spreadsheet_id = sheets_service.create_user_spreadsheet(user["email"])

            # Save the spreadsheet ID to the database
            success = db_service.save_spreadsheet_id(user["id"], spreadsheet_id)
            if not success:
                raise HTTPException(status_code=500, detail="Erro ao salvar ID da planilha no banco de dados")

        # Initialize transaction service
        transaction_service = TransactionService(spreadsheet_id)

        # Get transactions by category
        transactions = transaction_service.get_transactions_by_category(categoria)

        # Log the transaction operation
        monitoring_service.log_transaction_operation(
            user_id=user["id"],
            operation=f"get_transactions_by_category_{categoria}",
            success=True,
            details={
                "categoria": categoria,
                "transaction_count": len(transactions)
            }
        )

        return {
            "transactions": transactions,
            "count": len(transactions),
            "categoria": categoria,
            "user_id": user["id"]
        }
    except HTTPException:
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation=f"get_transactions_by_category_{categoria}",
            success=False,
            details={
                "error": "HTTP exception occurred"
            }
        )
        raise
    except Exception as e:
        logger.error(f"Error getting transactions by category: {str(e)}")
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation=f"get_transactions_by_category_{categoria}",
            success=False,
            details={
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao obter transações por categoria: {str(e)}")

@router.get("/tipo/{tipo}")
def get_transacoes_por_tipo(tipo: TransactionType, user=Depends(get_current_user)):
    """Get transactions filtered by type (expense or income)."""
    try:
        # Initialize database service to get user's spreadsheet ID
        db_service = DatabaseService()

        # Get user's spreadsheet ID from the database
        spreadsheet_id = db_service.get_spreadsheet_id(user["id"])
        if not spreadsheet_id:
            # Create a new spreadsheet if one doesn't exist
            from backend.services.google_sheets_service import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            spreadsheet_id = sheets_service.create_user_spreadsheet(user["email"])

            # Save the spreadsheet ID to the database
            success = db_service.save_spreadsheet_id(user["id"], spreadsheet_id)
            if not success:
                raise HTTPException(status_code=500, detail="Erro ao salvar ID da planilha no banco de dados")

        # Initialize transaction service
        transaction_service = TransactionService(spreadsheet_id)

        # Get transactions by type
        transactions = transaction_service.get_transactions_by_type(tipo)

        # Log the transaction operation
        monitoring_service.log_transaction_operation(
            user_id=user["id"],
            operation=f"get_transactions_by_type_{tipo.value}",
            success=True,
            details={
                "tipo": tipo.value,
                "transaction_count": len(transactions)
            }
        )

        return {
            "transactions": transactions,
            "count": len(transactions),
            "tipo": tipo.value,
            "user_id": user["id"]
        }
    except HTTPException:
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation=f"get_transactions_by_type_{tipo.value}",
            success=False,
            details={
                "error": "HTTP exception occurred"
            }
        )
        raise
    except Exception as e:
        logger.error(f"Error getting transactions by type: {str(e)}")
        # Log the error
        monitoring_service.log_transaction_operation(
            user_id=user.get("id", "unknown"),
            operation=f"get_transactions_by_type_{tipo.value}",
            success=False,
            details={
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Erro ao obter transações por tipo: {str(e)}")
