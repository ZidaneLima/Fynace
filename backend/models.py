from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from backend.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    refresh_token_encrypted = Column(String, nullable=True)
    spreadsheet_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    google_token = Column(JSON, nullable=True)
