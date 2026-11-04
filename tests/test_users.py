from sqlalchemy import select

from app.models import User
from app.security import hash_password, verify_password


def register(client, email="abhi@example.com", password="supersecret1"):
    return client.post("/api/auth/register", json={"email": email, "password": password})


def test_register_hides_the_password(client):
    res = register(client)
    assert res.status_code == 201
    body = res.json()
    assert "password" not in body
    assert "password_hash" not in body


def test_database_stores_a_hash_not_the_password(client, db):
    register(client)
    user = db.scalar(select(User))
    assert user.password_hash != "supersecret1"
    assert user.password_hash.startswith("$2b$")


def test_same_password_gives_different_hashes():
    assert hash_password("supersecret1") != hash_password("supersecret1")


def test_verify_password():
    stored = hash_password("supersecret1")
    assert verify_password("supersecret1", stored)
    assert not verify_password("wrongpassword", stored)


def test_duplicate_email_is_409_even_with_capitals(client):
    register(client, email="abhi@example.com")
    res = register(client, email="ABHI@Example.com")
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "conflict"


def test_short_password_is_422(client):
    assert register(client, password="short").status_code == 422


def test_bad_email_is_422(client):
    assert register(client, email="not-an-email").status_code == 422