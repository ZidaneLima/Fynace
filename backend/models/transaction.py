from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    expense = "despesa"
    income = "ganho"


class TransactionBase(BaseModel):
    descricao: str
    valor: float
    tipo: TransactionType
    categoria: str
    data: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: str
    data: datetime # type: ignore
    spreadsheet_id: str
    user_id: str

    class Config:
        from_attributes = True


class User(BaseModel):
    id: str
    email: str
    spreadsheet_id: Optional[str] = None

    class Config:
        from_attributes = True


class Summary(BaseModel):
    total_ganhos: float
    total_despesas: float
    saldo: float
    detalhes: List[dict]