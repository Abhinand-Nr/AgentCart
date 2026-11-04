from decimal import Decimal

import pytest

from app.errors import BadRequestError, NotFoundError
from app.services import cart as cart_service


def test_empty_cart(db, user):
    cart = cart_service.get_cart(db, user.id)
    assert cart["items"] == []
    assert cart["total"] == Decimal("0")


def test_total_adds_up_lines(db, user, products):
    shoes, socks, _ = products
    cart_service.add_item(db, user.id, shoes.id, 2)
    cart = cart_service.add_item(db, user.id, socks.id, 3)
    assert cart["total"] == Decimal("5695")
    assert cart["item_count"] == 5


def test_adding_same_product_twice_merges(db, user, products):
    shoes = products[0]
    cart_service.add_item(db, user.id, shoes.id, 1)
    cart = cart_service.add_item(db, user.id, shoes.id, 2)
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 3


def test_can_add_exactly_the_stock(db, user, products):
    cart = cart_service.add_item(db, user.id, products[2].id, 2)
    assert cart["item_count"] == 2


def test_cannot_add_more_than_stock(db, user, products):
    with pytest.raises(BadRequestError):
        cart_service.add_item(db, user.id, products[2].id, 3)


def test_remove_item(db, user, products):
    cart = cart_service.add_item(db, user.id, products[0].id, 1)
    cart = cart_service.remove_item(db, user.id, cart["items"][0]["id"])
    assert cart["items"] == []


def test_remove_missing_line_raises(db, user):
    with pytest.raises(NotFoundError):
        cart_service.remove_item(db, user.id, 999)
        