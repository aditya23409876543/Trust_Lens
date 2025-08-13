from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import require_role

router = APIRouter()

@router.get("")
def list_flags(status: str | None = None, entity_type: str | None = None, db: Session = Depends(get_db), user=Depends(require_role(models.Role.ADMIN))):
    q = db.query(models.Flag)
    if status:
        q = q.filter_by(status=models.FlagStatus(status))
    if entity_type:
        q = q.filter_by(entity_type=models.EntityType(entity_type))
    return q.order_by(models.Flag.created_at.desc()).all()

@router.post("/scan")
def trigger_scan(db: Session = Depends(get_db), user=Depends(require_role(models.Role.ADMIN))):
    return {"queued": True}

@router.patch("/{flag_id}")
def update_flag(flag_id: str, status: str, db: Session = Depends(get_db), user=Depends(require_role(models.Role.ADMIN))):
    fl = db.get(models.Flag, flag_id)
    if not fl:
        return {"updated": False}
    fl.status = models.FlagStatus(status)
    db.commit()
    return {"updated": True}
