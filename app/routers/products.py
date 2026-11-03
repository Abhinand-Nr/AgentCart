from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProductOut, ProductPage
from app.services import products as product_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductPage)
def list_products(
    q: str | None = None,
    category: str | None = None,
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    sort: Literal["name", "price", "stock"] = "name",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items, total = product_service.list_products(
        db,
        q=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        order=order,
        page=page,
        size=size,
    )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)