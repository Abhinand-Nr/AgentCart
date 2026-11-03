from decimal import Decimal

import pytest

from app.errors import BadRequestError, NotFoundError
from app.services import cart as cart_service


def test_empty_cart(db):
    cart = cart_service.get_cart(db)
    assert cart["items"] == []
    assert cart["total"] == Decimal("0")


def test_total_adds_up_lines(db, products):
    # Arrange
    shoes, socks, _ = products
    # Act
    cart_service.add_item(db, shoes.id, 2)
    cart = cart_service.add_item(db, socks.id, 3)
    # Assert: 2 x 2399 + 3 x 299
    assert cart["total"] == Decimal("5695")
    assert cart["item_count"] == 5


def test_adding_same_product_twice_merges(db, products):
    shoes = products[0]
    cart_service.add_item(db, shoes.id, 1)
    cart = cart_service.add_item(db, shoes.id, 2)
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 3


def test_can_add_exactly_the_stock(db, products):
    watch = products[2]  # stock is 2
    cart = cart_service.add_item(db, watch.id, 2)
    assert cart["item_count"] == 2


def test_cannot_add_more_than_stock(db, products):
    watch = products[2]  # stock is 2
    with pytest.raises(BadRequestError):
        cart_service.add_item(db, watch.id, 3)


def test_remove_item(db, products):
    cart = cart_service.add_item(db, products[0].id, 1)
    line_id = cart["items"][0]["id"]
    cart = cart_service.remove_item(db, line_id)
    assert cart["items"] == []


def test_remove_missing_line_raises(db):
    with pytest.raises(NotFoundError):
        cart_service.remove_item(db, 999)