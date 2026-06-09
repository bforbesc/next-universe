import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def pytest_configure(config):
    # Must run before app modules are imported anywhere.
    os.environ["DATABASE_URL"] = "sqlite:///" + str(BACKEND_DIR / "test.db")
    os.environ.pop("ANTHROPIC_API_KEY", None)
    db_file = BACKEND_DIR / "test.db"
    if db_file.exists():
        db_file.unlink()


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def student_id(client):
    resp = client.post(
        "/api/students",
        json={
            "name": "Ada",
            "age": 12,
            "interests": ["space", "rockets"],
            "prior_knowledge": "none",
            "difficulty_preference": "standard",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.fixture()
def adventure(client, student_id):
    resp = client.post("/api/adventures", json={"student_id": student_id})
    assert resp.status_code == 201, resp.text
    return resp.json()
