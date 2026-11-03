import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessaoTeste = sessionmaker(bind=engine)


def sobrescrever_get_db():
    db = SessaoTeste()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = sobrescrever_get_db


@pytest.fixture(autouse=True)
def resetar_banco():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def cliente():
    return TestClient(app)
