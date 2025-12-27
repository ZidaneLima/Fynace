"""Utility functions for error handling and validation."""
from fastapi import HTTPException
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def validate_transaction_data(data: Dict[str, Any]) -> bool:
    """Validate transaction data before processing."""
    required_fields = ["descricao", "valor", "tipo", "categoria"]
    
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Campo obrigatório '{field}' ausente")
    
    # Validate valor is a positive number
    valor = data.get("valor")
    if not isinstance(valor, (int, float)) or valor <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser um número positivo")
    
    # Validate tipo is either 'despesa' or 'ganho'
    tipo = data.get("tipo")
    if tipo not in ["despesa", "ganho"]:
        raise HTTPException(status_code=400, detail="Tipo deve ser 'despesa' ou 'ganho'")
    
    # Validate descricao is not empty
    descricao = data.get("descricao")
    if not descricao or not descricao.strip():
        raise HTTPException(status_code=400, detail="Descrição não pode ser vazia")
    
    return True

def handle_error(error: Exception, context: str = "Operação") -> HTTPException:
    """Standardized error handling."""
    logger.error(f"Error in {context}: {str(error)}")
    return HTTPException(
        status_code=500,
        detail=f"Erro ao processar {context.lower()}: {str(error)}"
    )