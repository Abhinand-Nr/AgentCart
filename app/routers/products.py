
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import ProductOut, ProductPage

router = APIRouter(prefix="/api/products", tags=["products"])

SORT_COLUMNS = {
    "name": Product.name,
    "price": Product.price,
    "stock": Product.stock,
}


@router.get("", response_model=ProductPage)
def list_products(
    q: str | None = None,
    category: str | None = None,
    sort: Literal["name", "price", "stock"] = "name",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = select(Product)
    if q:
        query = query.where(Product.name.ilike(f"%{q}%"))
    if category:
        query = query.where(Product.category == category)

    total = db.scalar(select(func.count()).select_from(query.subquery()))

    column = SORT_COLUMNS[sort]
    direction = column.desc() if order == "desc" else column.asc()
    query = query.order_by(direction, Product.id)
    query = query.offset((page - 1) * size).limit(size)

    items = db.scalars(query).all()
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product