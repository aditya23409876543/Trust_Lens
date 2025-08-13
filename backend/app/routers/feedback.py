from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
from ..utils import run_flagging_for_product, run_flagging_for_seller_product

router = APIRouter()

@router.post("", response_model=schemas.FeedbackOut)
def submit_feedback(payload: schemas.FeedbackIn, db: Session = Depends(get_db)):
    buyer = db.get(models.Buyer, payload.buyer_id)
    product = db.get(models.Product, payload.product_id)
    seller = db.get(models.Seller, payload.seller_id)
    if not all([buyer, product, seller]):
        raise HTTPException(status_code=400, detail="Invalid buyer/product/seller")

    sp = db.query(models.SellerProduct).filter_by(seller_id=seller.id, product_id=product.id).first()
    fb = models.Feedback(buyer_id=buyer.id, product_id=product.id, seller_id=seller.id,
                         seller_product_id=sp.id if sp else None, rating=payload.rating, comment=payload.comment)
    db.add(fb)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate feedback for this buyer/product/seller")
    db.refresh(fb)

    run_flagging_for_seller_product(db, seller.id, product.id)
    run_flagging_for_product(db, product.id)
    return fb

@router.get("", response_model=List[schemas.FeedbackOut])
def list_feedback(product_id: Optional[str] = None, seller_id: Optional[str] = None, buyer_id: Optional[str] = None,
                  page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    q = db.query(models.Feedback)
    if product_id:
        q = q.filter_by(product_id=product_id)
    if seller_id:
        q = q.filter_by(seller_id=seller_id)
    if buyer_id:
        q = q.filter_by(buyer_id=buyer_id)
    q = q.order_by(models.Feedback.created_at.desc())
    items = q.offset((page-1)*page_size).limit(page_size).all()
    return items
