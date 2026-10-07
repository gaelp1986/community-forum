import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db"),
        "SECRET_KEY": "test",
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def register(self, username="alice", password="secret"):
        return self._client.post("/register", data={"username": username, "password": password})

    def login(self, username="alice", password="secret"):
        return self._client.post("/login", data={"username": username, "password": password})

    def logout(self):
        return self._client.get("/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
