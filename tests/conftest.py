import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

URL_BANCO_TESTE = "sqlite:///:memory:"

engine = create_engine(
    URL_BANCO_TESTE,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessaoTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    yield


@pytest.fixture
def cliente():
    return TestClient(app)


@pytest.fixture
def criar_quarto(cliente):
    def _criar_quarto(**sobrescritas):
        payload = {
            "number": "101",
            "room_type": "standard",
            "price_per_night": 150.0,
            "capacity": 2,
        }
        payload.update(sobrescritas)
        resposta = cliente.post("/rooms", json=payload)
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar_quarto
