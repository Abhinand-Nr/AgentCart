from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import BadRequestError, NotFoundError
from app.models import Product

SORT_COLUMNS = {
    "name": Product.name,
    "price": Product.price,
    "stock": Product.stock,
}


def list_products(
    db: Session,
    q: str | None,
    category: str | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    sort: str,
    order: str,
    page: int,
    size: int,
) -> tuple[list[Product], int]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise BadRequestError("min_price can't be bigger than max_price")

    query = select(Product)
    if q:
        query = query.where(Product.name.ilike(f"%{q}%"))
    if category:
        query = query.where(Product.category == category)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)

    total = db.scalar(select(func.count()).select_from(query.subquery()))

    column = SORT_COLUMNS[sort]
    direction = column.desc() if order == "desc" else column.asc()
    query = query.order_by(direction, Product.id)
    query = query.offset((page - 1) * size).limit(size)

    items = list(db.scalars(query).all())
    return items, total


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} not found")
    return product