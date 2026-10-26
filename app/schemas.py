from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    category: str
    stock: int
    description: str


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    size: int