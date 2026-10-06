import os
import sqlite3
import tempfile

import pytest

# app.py reads these when it is imported, so set them first.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_PATH", os.path.join(tempfile.gettempdir(), "forum-import.db"))

import app as forum  # noqa: E402


@pytest.fixture
def client(tmp_path):
    # Give every test its own empty database.
    forum.DATABASE = str(tmp_path / "test.db")
    forum.init_db()
    forum.app.config["TESTING"] = True
    with forum.app.test_client() as client:
        yield client


def register(client, username="alice", password="pw123"):
    return client.post("/register", data={"username": username, "password": password})


def login(client, username="alice", password="pw123"):
    return client.post("/login", data={"username": username, "password": password})


def test_register_then_login(client):
    register(client)
    response = login(client)
    assert response.status_code == 302  # redirected to the feed


def test_duplicate_username_is_rejected(client):
    register(client)
    response = register(client)
    assert b"already taken" in response.data


def test_wrong_password_is_rejected(client):
    register(client)
    response = login(client, password="wrong")
    assert b"Invalid username or password" in response.data


def test_password_is_stored_hashed(client):
    register(client, password="pw123")
    db = sqlite3.connect(forum.DATABASE)
    stored = db.execute("SELECT password_hash FROM users").fetchone()[0]
    db.close()
    assert stored != "pw123"


def test_posting_requires_login(client):
    response = client.post("/", data={"content": "hello"})
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_author_comes_from_session_not_form(client):
    register(client, "alice")
    register(client, "bob")
    login(client, "alice")
    # Try to sneak another user's identity into the form.
    client.post("/", data={"content": "who wrote this?", "username": "bob", "user_id": "2"})
    db = sqlite3.connect(forum.DATABASE)
    author = db.execute(
        "SELECT users.username FROM posts JOIN users ON posts.user_id = users.id"
    ).fetchone()[0]
    db.close()
    assert author == "alice"


def test_post_length_limit(client):
    register(client)
    login(client)
    response = client.post("/", data={"content": "x" * (forum.MAX_POST_LENGTH + 1)})
    assert b"at most" in response.data


def test_rate_limit(client):
    register(client)
    login(client)
    for i in range(forum.POST_LIMIT):
        client.post("/", data={"content": f"post {i}"})
    response = client.post("/", data={"content": "one too many"})
    assert b"Try again in a few minutes" in response.data
