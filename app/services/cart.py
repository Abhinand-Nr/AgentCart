from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.errors import BadRequestError, NotFoundError
from app.models import CartItem
from app.services import products as product_service


def get_cart(db: Session) -> dict:
    query = (
        select(CartItem)
        .options(selectinload(CartItem.product))
        .order_by(CartItem.id)
    )
    items = db.scalars(query).all()

    lines = []
    total = Decimal("0.00")
    count = 0
    for item in items:
        line_total = item.product.price * item.quantity
        lines.append({
            "id": item.id,
            "product": item.product,
            "quantity": item.quantity,
            "line_total": line_total,
        })
        total += line_total
        count += item.quantity

    return {"items": lines, "item_count": count, "total": total}


def add_item(db: Session, product_id: int, quantity: int) -> dict:
    product = product_service.get_product(db, product_id)  # 404 if missing

    item = db.scalar(select(CartItem).where(CartItem.product_id == product_id))
    already = item.quantity if item else 0
    if already + quantity > product.stock:
        raise BadRequestError(f"Only {product.stock} of {product.name} in stock")

    if item:
        item.quantity = already + quantity
    else:
        db.add(CartItem(product_id=product_id, quantity=quantity))
    db.commit()
    return get_cart(db)


def _get_item(db: Session, item_id: int) -> CartItem:
    item = db.get(CartItem, item_id)
    if item is None:
        raise NotFoundError(f"Cart item {item_id} not found")
    return item


def update_quantity(db: Session, item_id: int, quantity: int) -> dict:
    item = _get_item(db, item_id)
    if quantity > item.product.stock:
        raise BadRequestError(f"Only {item.product.stock} of {item.product.name} in stock")
    item.quantity = quantity
    db.commit()
    return get_cart(db)


def remove_item(db: Session, item_id: int) -> dict:
    item = _get_item(db, item_id)
    db.delete(item)
    db.commit()
    return get_cart(db)