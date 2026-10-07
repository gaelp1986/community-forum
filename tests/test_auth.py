import sqlite3

from flask import session


def test_register_page_loads(client):
    assert client.get("/register").status_code == 200


def test_register_creates_user(client, auth, app):
    response = auth.register()
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    db = sqlite3.connect(app.config["DATABASE"])
    row = db.execute("SELECT password_hash FROM users WHERE username = 'alice'").fetchone()
    db.close()
    assert row is not None
    # The password itself must never be stored.
    assert row[0] != "secret"


def test_register_rejects_duplicate_username(auth):
    auth.register()
    response = auth.register()
    assert response.status_code == 200
    assert b"That username is already taken." in response.data


def test_register_requires_username_and_password(auth):
    response = auth.register(username="   ", password="secret")
    assert b"Username and password are required." in response.data
    response = auth.register(username="bob", password="")
    assert b"Username and password are required." in response.data


def test_login_sets_session(client, auth):
    auth.register()
    with client:
        response = auth.login()
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
        assert session["username"] == "alice"


def test_login_rejects_wrong_password(auth):
    auth.register()
    response = auth.login(password="wrong")
    assert b"Invalid username or password." in response.data


def test_login_rejects_unknown_user(auth):
    response = auth.login(username="nobody")
    assert b"Invalid username or password." in response.data


def test_logout_clears_session(client, auth):
    auth.register()
    auth.login()
    with client:
        auth.logout()
        assert "user_id" not in session
