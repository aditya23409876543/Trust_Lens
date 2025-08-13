from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from . import models
from .database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas
class FeedbackBase(BaseModel):
    buyer_id: int
    product_id: int
    seller_id: int
    rating: float
    comment: str

class FeedbackOut(FeedbackBase):
    id: int
    date: str
    class Config:
        orm_mode = True

# Sample products
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 19.99},
    {"id": 2, "name": "Mechanical Keyboard", "price": 59.99},
    {"id": 3, "name": "Gaming Headset", "price": 39.99},
]

# Routes
@app.get("/api/v1/products/")
def get_products():
    return products

@app.get("/api/v1/products/{product_id}/feedback", response_model=List[FeedbackOut])
def get_product_feedback(product_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(models.Feedback).filter(models.Feedback.product_id == product_id).all()
    return feedbacks

@app.post("/api/v1/feedback", response_model=FeedbackOut)
def create_feedback(feedback: FeedbackBase, db: Session = Depends(get_db)):
    new_feedback = models.Feedback(**feedback.dict(), date=datetime.utcnow())
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback
