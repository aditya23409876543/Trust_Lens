from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import hash_password, verify_password, create_access_token
from ..schemas import LoginIn, TokenOut

router = APIRouter()

@router.post("/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email="admin@example.com").first():
        return {"ok": True}
    admin = models.User(email="admin@example.com", password_hash=hash_password("admin123"), role=models.Role.ADMIN)
    db.add(admin)
    db.commit()
    return {"email": admin.email, "password": "admin123"}

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, user.role.value, user.seller_id)
    return {"access_token": token}
