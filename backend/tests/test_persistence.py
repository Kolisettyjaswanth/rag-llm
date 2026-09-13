import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

os.environ.setdefault("POSTGRES_DB", "lenny_growth_assistant")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_HOST", "postgres")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@postgres:5432/lenny_growth_assistant_test"

from app.db.database import engine  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)

TEST_DB_NAME = "lenny_growth_assistant_test"
TEST_DB_URL = os.environ["DATABASE_URL"]
ADMIN_DB_URL = "postgresql+psycopg://postgres:postgres@postgres:5432/postgres"
admin_engine = create_engine(ADMIN_DB_URL, pool_pre_ping=True)
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)


@pytest.fixture(scope="module", autouse=True)
def ensure_test_database():
    with admin_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
            {"database_name": TEST_DB_NAME},
        )
        exists = result.fetchone() is not None

    if not exists:
        with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    command.upgrade(alembic_cfg, "head")

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    yield


def test_create_and_retrieve_session():
    response = client.post("/api/sessions", json={"title": "Session 1"})
    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Session 1"
    assert "id" in payload

    session_id = payload["id"]
    detail = client.get(f"/api/sessions/{session_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == session_id


def test_create_and_list_messages_for_session():
    session = client.post("/api/sessions", json={"title": "Chat"}).json()
    session_id = session["id"]

    create = client.post(f"/api/sessions/{session_id}/messages", json={"role": "user", "content": "hello"})
    assert create.status_code == 201

    messages = client.get(f"/api/sessions/{session_id}/messages")
    assert messages.status_code == 200
    assert len(messages.json()) >= 1
    assert messages.json()[0]["session_id"] == session_id


def test_session_isolation():
    session_a = client.post("/api/sessions", json={"title": "A"}).json()
    session_b = client.post("/api/sessions", json={"title": "B"}).json()

    client.post(f"/api/sessions/{session_a['id']}/messages", json={"role": "user", "content": "A1"})
    client.post(f"/api/sessions/{session_b['id']}/messages", json={"role": "user", "content": "B1"})

    a_messages = client.get(f"/api/sessions/{session_a['id']}/messages").json()
    b_messages = client.get(f"/api/sessions/{session_b['id']}/messages").json()

    assert all(message["session_id"] == session_a["id"] for message in a_messages)
    assert all(message["session_id"] == session_b["id"] for message in b_messages)
    assert any("A1" in message["content"] for message in a_messages)
    assert any("B1" in message["content"] for message in b_messages)


def test_invalid_session_404():
    response = client.get("/api/sessions/999999")
    assert response.status_code == 404


def test_invalid_role_rejected():
    session = client.post("/api/sessions", json={"title": "Role test"}).json()
    response = client.post(f"/api/sessions/{session['id']}/messages", json={"role": "invalid", "content": "hello"})
    assert response.status_code == 422


def test_empty_message_content_rejected():
    session = client.post("/api/sessions", json={"title": "Empty content"}).json()
    response = client.post(f"/api/sessions/{session['id']}/messages", json={"role": "user", "content": ""})
    assert response.status_code == 422
