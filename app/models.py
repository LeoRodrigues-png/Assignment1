from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    product_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    unit_price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    description: str = Field(..., min_length=1)


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

