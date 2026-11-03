from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CartItemAdd, CartItemUpdate, CartOut
from app.services import cart as cart_service

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=CartOut)
def view_cart(db: Session = Depends(get_db)):
    return cart_service.get_cart(db)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(body: CartItemAdd, db: Session = Depends(get_db)):
    return cart_service.add_item(db, body.product_id, body.quantity)


@router.patch("/items/{item_id}", response_model=CartOut)
def change_quantity(item_id: int, body: CartItemUpdate, db: Session = Depends(get_db)):
    return cart_service.update_quantity(db, item_id, body.quantity)


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    return cart_service.remove_item(db, item_id)