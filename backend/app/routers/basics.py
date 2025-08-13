from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()

@router.post("/buyers", response_model=schemas.BuyerOut)
def create_buyer(buyer: schemas.BuyerIn, db: Session = Depends(get_db)):
    b = models.Buyer(email=buyer.email)
    db.add(b); db.commit(); db.refresh(b)
    return b

@router.post("/sellers", response_model=schemas.SellerOut)
def create_seller(seller: schemas.SellerIn, db: Session = Depends(get_db)):
    s = models.Seller(name=seller.name)
    db.add(s); db.commit(); db.refresh(s)
    return s

@router.post("/products", response_model=schemas.ProductOut)
def create_product(p: schemas.ProductIn, db: Session = Depends(get_db)):
    pr = models.Product(name=p.name, sku=p.sku)
    db.add(pr); db.commit(); db.refresh(pr)
    return pr

@router.post("/seller-products")
def link_seller_product(seller_id: str, product_id: str, price_cents: int = 0, currency: str = "INR", db: Session = Depends(get_db)):
    sp = models.SellerProduct(seller_id=seller_id, product_id=product_id, price_cents=price_cents, currency=currency)
    db.add(sp); db.commit(); db.refresh(sp)
    return {"id": sp.id}
