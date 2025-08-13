from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: str
    password: str

class BuyerIn(BaseModel):
    email: Optional[str] = None

class BuyerOut(BaseModel):
    id: str
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SellerIn(BaseModel):
    name: str

class SellerOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class ProductIn(BaseModel):
    name: str
    sku: Optional[str] = None

class ProductOut(BaseModel):
    id: str
    name: str
    sku: Optional[str] = None

    class Config:
        from_attributes = True

class FeedbackIn(BaseModel):
    buyer_id: str
    product_id: str
    seller_id: str
    rating: int = Field(ge=1, le=5)
    comment: str
    date: Optional[datetime] = None

class FeedbackOut(BaseModel):
    id: str
    buyer_id: str
    product_id: str
    seller_id: str
    rating: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True

class AggregateOut(BaseModel):
    product_id: str
    avg_rating: float
    review_count: int
    last_reviewed_at: Optional[datetime] = None

class SellerAggregateOut(BaseModel):
    seller_id: str
    product_id: str
    avg_rating: float
    review_count: int
    last_reviewed_at: Optional[datetime] = None

class RecommendationOut(BaseModel):
    seller_id: str
    avg_rating: float
    review_count: int
    price_cents: int
    currency: str
    rationale: str

class FlagOut(BaseModel):
    id: str
    entity_type: str
    product_id: str | None = None
    seller_id: str | None = None
    seller_product_id: str | None = None
    severity: str
    reason_code: str | None = None
    status: str
