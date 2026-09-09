import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite por padrão (facilita rodar localmente e no CI sem dependências externas).
# Em produção/CD, pode ser trocado por Postgres via variável de ambiente DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hotel.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
