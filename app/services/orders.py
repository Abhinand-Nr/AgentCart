from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.errors import BadRequestError, ConflictError, NotFoundError
from app.models import CartItem, Order, OrderItem, Product


def checkout(db: Session, user_id: int) -> Order:
    try:
        cart_items = db.scalars(
            select(CartItem).where(CartItem.user_id == user_id)
        ).all()
        if not cart_items:
            raise BadRequestError("Your cart is empty")

        # Lock these product rows. Anyone else checking out the same
        # products waits here until we commit or roll back.
        product_ids = [item.product_id for item in cart_items]
        locked = db.scalars(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).all()
        products = {p.id: p for p in locked}

        order = Order(user_id=user_id, total=Decimal("0.00"))
        total = Decimal("0.00")
        for item in cart_items:
            product = products[item.product_id]
            if product.stock < item.quantity:
                raise ConflictError(f"Only {product.stock} of {product.name} left")

            product.stock -= item.quantity
            order.items.append(OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=item.quantity,
            ))
            total += product.price * item.quantity

        order.total = total
        db.add(order)
        for item in cart_items:
            db.delete(item)

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order


def list_orders(db: Session, user_id: int) -> list[Order]:
    query = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
    )
    return list(db.scalars(query).all())


def get_order(db: Session, user_id: int, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user_id:
        raise NotFoundError(f"Order {order_id} not found")
    return order