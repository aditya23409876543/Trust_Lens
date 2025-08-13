from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..utils import seller_product_aggregate

router = APIRouter()

@router.get("/{seller_id}/products")
def seller_products(seller_id: str, db: Session = Depends(get_db)):
    if not db.get(models.Seller, seller_id):
        raise HTTPException(status_code=404, detail="Seller not found")
    sps = db.query(models.SellerProduct).filter_by(seller_id=seller_id).all()
    out = []
    for sp in sps:
        agg = seller_product_aggregate(db, seller_id, sp.product_id)
        agg["is_flagged"] = db.query(models.Flag).filter_by(seller_product_id=sp.id, status=models.FlagStatus.OPEN).first() is not None
        out.append(agg)
    return out

@router.get("/{seller_id}/products/{product_id}/feedback")
def seller_product_feedback(seller_id: str, product_id: str, db: Session = Depends(get_db)):
    if not db.get(models.Seller, seller_id) or not db.get(models.Product, product_id):
        raise HTTPException(status_code=404, detail="Not found")
    items = db.query(models.Feedback).filter_by(seller_id=seller_id, product_id=product_id).order_by(models.Feedback.created_at.desc()).all()
    return [{"id": f.id, "rating": f.rating, "comment": f.comment, "date": f.created_at.isoformat()} for f in items]
