from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import CartItemAdd, CartItemUpdate, CartOut
from app.services import cart as cart_service

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=CartOut)
def view_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cart_service.get_cart(db, user.id)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    body: CartItemAdd,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.add_item(db, user.id, body.product_id, body.quantity)


@router.patch("/items/{item_id}", response_model=CartOut)
def change_quantity(
    item_id: int,
    body: CartItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.update_quantity(db, user.id, item_id, body.quantity)


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_from_cart(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.remove_item(db, user.id, item_id)