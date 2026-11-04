import threading
from decimal import Decimal

from sqlalchemy import func, select

from app.errors import ConflictError
from app.models import CartItem, Order, Product, User
from app.services import orders as order_service


def add(client, product_id, quantity):
    return client.post("/api/cart/items", json={"product_id": product_id, "quantity": quantity})


def test_checkout_creates_order_and_empties_cart(auth_client, products):
    shoes = products[0]  # stock 5
    add(auth_client, shoes.id, 2)

    res = auth_client.post("/api/orders/checkout")
    assert res.status_code == 201
    assert Decimal(res.json()["total"]) == Decimal("4798")
    assert auth_client.get("/api/cart").json()["items"] == []
    assert auth_client.get(f"/api/products/{shoes.id}").json()["stock"] == 3


def test_empty_cart_checkout_is_400(auth_client):
    assert auth_client.post("/api/orders/checkout").status_code == 400


def test_not_enough_stock_is_409_and_nothing_changes(auth_client, db, products):
    watch = products[2]  # stock 2
    add(auth_client, watch.id, 2)

    watch.stock = 1  # someone else bought one in the meantime
    db.commit()

    res = auth_client.post("/api/orders/checkout")
    assert res.status_code == 409
    db.refresh(watch)
    assert watch.stock == 1                                      # not touched
    assert len(auth_client.get("/api/cart").json()["items"]) == 1  # cart kept
    assert db.scalar(select(func.count()).select_from(Order)) == 0  # no order


def test_order_keeps_the_price_paid(auth_client, db, products):
    shoes = products[0]
    add(auth_client, shoes.id, 1)
    order_id = auth_client.post("/api/orders/checkout").json()["id"]

    shoes.price = Decimal("9999.00")  # price goes up later
    db.commit()

    order = auth_client.get(f"/api/orders/{order_id}").json()
    assert Decimal(order["items"][0]["unit_price"]) == Decimal("2399")


def test_cannot_see_someone_elses_order(auth_client, db, products):
    add(auth_client, products[0].id, 1)
    order_id = auth_client.post("/api/orders/checkout").json()["id"]

    other = User(email="friend@example.com", password_hash="x")
    db.add(other)
    db.commit()
    from app.security import create_access_token
    auth_client.headers["Authorization"] = f"Bearer {create_access_token(other.id)}"

    assert auth_client.get(f"/api/orders/{order_id}").status_code == 404


def test_two_buyers_one_last_unit(db, session_factory):
    # Arrange: one watch left, two buyers with it in their carts
    watch = Product(name="Last Watch", price=Decimal("4999.00"), category="Electronics",
                    stock=1, description="Only one left")
    buyers = [User(email=f"buyer{i}@example.com", password_hash="x") for i in range(2)]
    db.add_all([watch, *buyers])
    db.commit()
    for b in buyers:
        db.add(CartItem(user_id=b.id, product_id=watch.id, quantity=1))
    db.commit()
    buyer_ids = [b.id for b in buyers]
    watch_id = watch.id
    db.close()

    # Act: both check out at the same moment, each with its own session
    start_together = threading.Barrier(2)
    results = []

    def buy(user_id):
        session = session_factory()
        try:
            start_together.wait()
            order_service.checkout(session, user_id)
            results.append("ok")
        except ConflictError:
            results.append("sold out")
        finally:
            session.close()

    threads = [threading.Thread(target=buy, args=(uid,)) for uid in buyer_ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Assert: exactly one winner, stock 0, one order
    assert sorted(results) == ["ok", "sold out"]
    with session_factory() as check:
        assert check.get(Product, watch_id).stock == 0
        assert check.scalar(select(func.count()).select_from(Order)) == 1