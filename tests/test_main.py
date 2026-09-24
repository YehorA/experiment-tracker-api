import os
import pytest

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

@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

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
    assert data["id"] == 1

def test_get_missing_project():
    response = client.get("/projects/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

def test_create_project_without_name():
    response = client.post(
        "/projects",
        json={
            "description": "Missing name",
        },
    )

    assert response.status_code == 422

def test_create_and_get_project():
    create_response = client.post(
        "/projects",
        json={
            "name": "Workflow Project",
            "description": "Testing create then get",
        },
    )

    project_id = create_response.json()["id"]

    get_response = client.get(f"/projects/{project_id}")
    data = get_response.json()

    assert get_response.status_code == 200
    assert data["name"] == "Workflow Project"
    assert data["description"] == "Testing create then get"
    assert data["id"] == project_id

def test_delete_project():
    create_response = client.post(
        "/projects",
        json={
            "name": "Project to Delete",
            "description": "Testing deletion",
        },
    )

    project_id = create_response.json()["id"]

    delete_response = client.delete(f"/projects/{project_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Project deleted"}

    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404