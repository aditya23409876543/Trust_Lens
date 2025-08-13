from sqlalchemy.orm import Session
from sqlalchemy import func, select
from . import models
from datetime import datetime, timedelta, timezone

def product_aggregate(db: Session, product_id: str):
    q = select(func.avg(models.Feedback.rating), func.count(models.Feedback.id), func.max(models.Feedback.created_at)).where(models.Feedback.product_id==product_id)
    avg, count, last = db.execute(q).one()
    return {
        "product_id": product_id,
        "avg_rating": float(avg or 0),
        "review_count": int(count or 0),
        "last_reviewed_at": last
    }

def seller_product_aggregate(db: Session, seller_id: str, product_id: str):
    q = select(func.avg(models.Feedback.rating), func.count(models.Feedback.id), func.max(models.Feedback.created_at)).where(
        models.Feedback.product_id==product_id, models.Feedback.seller_id==seller_id)
    avg, count, last = db.execute(q).one()
    return {
        "seller_id": seller_id,
        "product_id": product_id,
        "avg_rating": float(avg or 0),
        "review_count": int(count or 0),
        "last_reviewed_at": last
    }

def run_flagging_for_product(db: Session, product_id: str):
    from sqlalchemy import and_
    sellers = db.query(models.SellerProduct).filter(models.SellerProduct.product_id==product_id, models.SellerProduct.is_active==True).all()
    if not sellers:
        return None
    threshold_count = int(0.6 * len(sellers)) or 1
    poor = 0
    since = datetime.now(timezone.utc) - timedelta(days=30)
    for sp in sellers:
        q = db.query(models.Feedback).filter(
            models.Feedback.product_id==product_id,
            models.Feedback.seller_id==sp.seller_id,
            models.Feedback.created_at>=since
        )
        ratings = [f.rating for f in q]
        if len(ratings) >= 10 and (sum(ratings)/len(ratings)) <= 2.5:
            poor += 1
    if poor >= threshold_count:
        flag = models.Flag(entity_type=models.EntityType.PRODUCT, product_id=product_id, severity=models.Severity.HIGH, reason_code="LOW_QUALITY_PRODUCT", details={"poor_sellers": poor, "total_sellers": len(sellers)})
        db.add(flag)
        db.commit()
        db.refresh(flag)
        return flag
    return None

def run_flagging_for_seller_product(db: Session, seller_id: str, product_id: str):
    since = datetime.now(timezone.utc) - timedelta(days=60)
    q = db.query(models.Feedback).filter(
        models.Feedback.product_id==product_id,
        models.Feedback.seller_id==seller_id,
        models.Feedback.created_at>=since
    )
    ratings = [f.rating for f in q]
    if len(ratings) >= 5 and (sum(ratings)/len(ratings)) <= 2.5:
        sp = db.query(models.SellerProduct).filter_by(seller_id=seller_id, product_id=product_id).first()
        sp_id = sp.id if sp else None
        flag = models.Flag(entity_type=models.EntityType.SELLER_PRODUCT, product_id=product_id, seller_id=seller_id, seller_product_id=sp_id, severity=models.Severity.MEDIUM, reason_code="POOR_SELLER_PERFORMANCE", details={"reviews": len(ratings)})
        db.add(flag)
        db.commit()
        db.refresh(flag)
        return flag
    return None

def recommend_sellers_for_product(db: Session, product_id: str, limit: int = 3):
    results = []
    sps = db.query(models.SellerProduct).filter_by(product_id=product_id, is_active=True).all()
    for sp in sps:
        q = db.query(models.Feedback).filter_by(product_id=product_id, seller_id=sp.seller_id)
        ratings = [f.rating for f in q]
        avg = sum(ratings)/len(ratings) if ratings else 0.0
        results.append({
            "seller_id": sp.seller_id,
            "avg_rating": avg,
            "review_count": len(ratings),
            "price_cents": sp.price_cents or 0,
            "currency": sp.currency,
            "rationale": "Higher-rated seller even if price is higher" if avg >= 4.0 else "Seller considered"
        })
    results.sort(key=lambda x: (-x["avg_rating"], -x["review_count"], x["price_cents"]))
    return results[:limit]
