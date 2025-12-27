from fastapi import APIRouter, Depends, HTTPException
from backend.auth_utils import get_current_user
from backend.services.google_sheets_service import GoogleSheetsService
from backend.models.transaction import Summary
from backend.database.database_service import DatabaseService
from backend.services.transaction_service import TransactionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def get_resumo(user=Depends(get_current_user)):
    try:
        # Initialize database service to get user's spreadsheet ID
        db_service = DatabaseService()

        # Get user's spreadsheet ID from the database
        spreadsheet_id = db_service.get_spreadsheet_id(user["id"])
        if not spreadsheet_id:
            # Create a new spreadsheet if one doesn't exist
            sheets_service = GoogleSheetsService()
            spreadsheet_id = sheets_service.create_user_spreadsheet(user["email"])

            # Save the spreadsheet ID to the database
            success = db_service.save_spreadsheet_id(user["id"], spreadsheet_id)
            if not success:
                raise HTTPException(status_code=500, detail="Erro ao salvar ID da planilha no banco de dados")

        # Initialize transaction service
        transaction_service = TransactionService(spreadsheet_id)

        # Get summary from Google Sheets using the transaction service
        summary_data = transaction_service.sheets_service.get_summary(spreadsheet_id)
        category_breakdown = transaction_service.sheets_service.get_category_breakdown(spreadsheet_id)

        summary = Summary(
            total_ganhos=summary_data["total_ganhos"],
            total_despesas=summary_data["total_despesas"],
            saldo=summary_data["saldo"],
            detalhes=category_breakdown
        )

        return {
            "total_ganhos": summary.total_ganhos,
            "total_despesas": summary.total_despesas,
            "saldo": summary.saldo,
            "detalhes": summary.detalhes,
            "user": user["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo: {str(e)}")
