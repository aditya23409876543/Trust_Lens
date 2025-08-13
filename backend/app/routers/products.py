from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..utils import product_aggregate, recommend_sellers_for_product

router = APIRouter()

@router.get("/{product_id}/feedback", response_model=schemas.AggregateOut)
def get_product_feedback(product_id: str, db: Session = Depends(get_db)):
    if not db.get(models.Product, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return product_aggregate(db, product_id)

@router.get("/{product_id}/sellers")
def list_sellers_for_product(product_id: str, db: Session = Depends(get_db)):
    if not db.get(models.Product, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    data = []
    sps = db.query(models.SellerProduct).filter_by(product_id=product_id, is_active=True).all()
    for sp in sps:
        ratings = [f.rating for f in db.query(models.Feedback).filter_by(product_id=product_id, seller_id=sp.seller_id)]
        avg = sum(ratings)/len(ratings) if ratings else 0.0
        count = len(ratings)
        flagged = db.query(models.Flag).filter_by(seller_product_id=sp.id, status=models.FlagStatus.OPEN).first() is not None
        data.append({
            "seller_id": sp.seller_id,
            "avg_rating": round(avg,2),
            "review_count": count,
            "price_cents": sp.price_cents or 0,
            "currency": sp.currency,
            "is_flagged": flagged
        })
    return {"product_id": product_id, "sellers": data}

@router.get("/{product_id}/recommendations", response_model=List[schemas.RecommendationOut])
def recommendations(product_id: str, db: Session = Depends(get_db)):
    if not db.get(models.Product, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return recommend_sellers_for_product(db, product_id)
