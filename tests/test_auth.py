from datetime import datetime, timedelta, timezone

import jwt

from app.models import User
from app.security import JWT_ALGORITHM, JWT_SECRET, create_access_token, hash_password


def login(client, email="abhi@example.com", password="supersecret1"):
    return client.post("/api/auth/login", data={"username": email, "password": password})


def test_login_returns_a_token(client, user):
    res = login(client)
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"


def test_wrong_password_is_401(client, user):
    assert login(client, password="wrongpassword").status_code == 401


def test_unknown_email_gives_the_same_message(client, user):
    wrong_pw = login(client, password="wrongpassword").json()
    no_user = login(client, email="nobody@example.com").json()
    assert wrong_pw == no_user


def test_me_with_token(client, user):
    token = login(client).json()["access_token"]
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "abhi@example.com"


def test_me_without_token_is_401(client):
    assert client.get("/api/auth/me").status_code == 401


def test_edited_token_is_rejected(client, user):
    token = create_access_token(user.id)
    broken = token[:-2] + ("aa" if not token.endswith("aa") else "bb")
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {broken}"})
    assert res.status_code == 401


def test_expired_token_is_rejected(client, user):
    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode({"sub": str(user.id), "exp": past}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


def test_users_cannot_touch_each_others_carts(auth_client, db, products):
    line_id = auth_client.post(
        "/api/cart/items", json={"product_id": products[0].id, "quantity": 1}
    ).json()["items"][0]["id"]

    friend = User(email="friend@example.com", password_hash=hash_password("supersecret1"))
    db.add(friend)
    db.commit()
    auth_client.headers["Authorization"] = f"Bearer {create_access_token(friend.id)}"

    assert auth_client.get("/api/cart").json()["items"] == []
    assert auth_client.delete(f"/api/cart/items/{line_id}").status_code == 404