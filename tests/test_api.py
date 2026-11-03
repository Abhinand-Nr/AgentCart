from decimal import Decimal


def test_list_products(client, products):
    res = client.get("/api/products")
    assert res.status_code == 200
    assert res.json()["total"] == 3


def test_missing_product_gives_clean_404(client):
    res = client.get("/api/products/999")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "not_found"


def test_bad_page_gives_422(client):
    res = client.get("/api/products?page=0")
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "validation_error"


def test_add_to_cart(client, products):
    shoes = products[0]
    res = client.post("/api/cart/items", json={"product_id": shoes.id, "quantity": 2})
    assert res.status_code == 201
    assert Decimal(res.json()["total"]) == Decimal("4798")


def test_add_zero_quantity_gives_422(client, products):
    res = client.post("/api/cart/items", json={"product_id": products[0].id, "quantity": 0})
    assert res.status_code == 422