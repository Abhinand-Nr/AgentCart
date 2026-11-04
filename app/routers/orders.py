from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import OrderOut
from app.services import orders as order_service

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.checkout(db, user.id)


@router.get("", response_model=list[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.list_orders(db, user.id)


@router.get("/{order_id}", response_model=OrderOut)
def one_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.get_order(db, user.id, order_id)