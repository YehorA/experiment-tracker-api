import os

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Experiment Tracker API"}

def test_create_project():
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "Created during testing",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "Test Project"
    assert data["description"] == "Created during testing"
    assert isinstance(data["id"], int)
    assert data["id"] > 0