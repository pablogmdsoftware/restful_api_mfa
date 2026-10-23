import pytest
import tempfile
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path
from app.main import app
from app.database import get_session

@pytest.fixture(scope="module")
def session():
    with tempfile.TemporaryDirectory() as temp_dir:
        sqlite_file_name = Path(temp_dir) / "test.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"

        connect_args = {"check_same_thread": False}
        engine = create_engine(sqlite_url, connect_args=connect_args)
        
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            yield session

@pytest.fixture(scope="module")
def client(session):

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def access_token(client):
    response = client.post(
        "/token",
        data={"username": "example@gmail.com", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]