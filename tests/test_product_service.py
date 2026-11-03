from decimal import Decimal

import pytest

from app.errors import BadRequestError, NotFoundError
from app.services import products as product_service


def list_products(db, **changes):
    args = dict(q=None, category=None, min_price=None, max_price=None,
                sort="name", order="asc", page=1, size=10)
    args.update(changes)
    return product_service.list_products(db, **args)


def test_filter_by_category(db, products):
    items, total = list_products(db, category="Sports")
    assert total == 1
    assert items[0].name == "Cotton Socks"


def test_sort_by_price_desc(db, products):
    items, _ = list_products(db, sort="price", order="desc")
    assert [p.name for p in items] == ["Smartwatch", "Running Shoes", "Cotton Socks"]


def test_second_page(db, products):
    items, total = list_products(db, size=2, page=2)
    assert total == 3
    assert len(items) == 1


def test_price_range(db, products):
    items, _ = list_products(db, min_price=Decimal("1000"), max_price=Decimal("3000"))
    assert [p.name for p in items] == ["Running Shoes"]


def test_min_bigger_than_max_is_rejected(db, products):
    with pytest.raises(BadRequestError):
        list_products(db, min_price=Decimal("3000"), max_price=Decimal("1000"))


def test_missing_product_raises(db):
    with pytest.raises(NotFoundError):
        product_service.get_product(db, 999)