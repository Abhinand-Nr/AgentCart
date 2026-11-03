from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

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

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, le=20)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=20)


class CartLine(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    line_total: Decimal


class CartOut(BaseModel):
    items: list[CartLine]
    item_count: int
    total: Decimal