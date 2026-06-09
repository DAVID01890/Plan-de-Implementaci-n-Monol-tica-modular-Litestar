import os
import tempfile
import uuid

from litestar.testing import TestClient

from src.entrypoint.app import create_app


def _client():
    os.environ.pop("TURSO_DATABASE_URL", None)
    os.environ.pop("TURSO_AUTH_TOKEN", None)
    os.environ.pop("SKIP_DB_INIT", None)
    db_path = os.path.join(tempfile.gettempdir(), f"test_auth_{uuid.uuid4().hex}.db")
    os.environ["SQLITE_PATH"] = db_path
    app = create_app()
    return TestClient(app)


def test_register_success() -> None:
    with _client() as client:
        response = client.post("/auth/register", json={"email": "new@example.com", "password": "pass123"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "new@example.com"


def test_register_duplicate_email() -> None:
    with _client() as client:
        client.post("/auth/register", json={"email": "dup@example.com", "password": "pass123"})
        response = client.post("/auth/register", json={"email": "dup@example.com", "password": "other456"})
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_invalid_email() -> None:
    with _client() as client:
        response = client.post("/auth/register", json={"email": "not-an-email", "password": "pass123"})
    assert response.status_code == 400


def test_login_success() -> None:
    with _client() as client:
        client.post("/auth/register", json={"email": "login@example.com", "password": "secret123"})
        response = client.post("/auth/login", json={"email": "login@example.com", "password": "secret123"})
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


def test_login_wrong_password() -> None:
    with _client() as client:
        client.post("/auth/register", json={"email": "wp@example.com", "password": "correct"})
        response = client.post("/auth/login", json={"email": "wp@example.com", "password": "wrong"})
    assert response.status_code == 401


def test_login_nonexistent_user() -> None:
    with _client() as client:
        response = client.post("/auth/login", json={"email": "nobody@example.com", "password": "anything"})
    assert response.status_code == 401


def test_login_invalid_email_format() -> None:
    with _client() as client:
        response = client.post("/auth/login", json={"email": "bad", "password": "x"})
    assert response.status_code == 400


def test_protected_route_without_token() -> None:
    with _client() as client:
        response = client.get("/proyectos")
    assert response.status_code == 401


def test_protected_route_with_invalid_token() -> None:
    with _client() as client:
        headers = {"Authorization": "Bearer invalid.jwt.token"}
        response = client.get("/proyectos", headers=headers)
    assert response.status_code == 401


def test_health_is_public() -> None:
    with _client() as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_routes_are_public() -> None:
    with _client() as client:
        reg = client.post("/auth/register", json={"email": "pub@example.com", "password": "x"})
        log = client.post("/auth/login", json={"email": "pub@example.com", "password": "x"})
    assert reg.status_code == 201
    assert log.status_code == 201
