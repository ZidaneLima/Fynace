from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.config import DATABASE_URL

# Cria o engine (funciona com SQLite, PostgreSQL, etc.)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependência de sessão (para usar nas rotas com FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Buscar usuário pelo e-mail usando SQLAlchemy ORM
def get_user_by_email(db: Session, email: str):
    from backend.models import User
    return db.query(User).filter(User.email == email).first()