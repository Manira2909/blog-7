from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Notification
from app.routes.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def create_notification(db: Session, user_id: int, message: str, type: str = "general"):
    n = Notification(user_id=user_id, message=message, type=type)
    db.add(n); db.commit(); db.refresh(n)
    return n

@router.get("/")
def get_my_notifications(db: Session = Depends(get_db), user = Depends(get_current_user)):
    notifs = db.query(Notification).filter(Notification.user_id==user.id).order_by(Notification.created_at.desc()).all()
    unread_count = db.query(Notification).filter(Notification.user_id==user.id, Notification.is_read==False).count()
    return {"notifications": notifs, "unread_count": unread_count}

@router.post("/{notif_id}/read")
def mark_read(notif_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id==notif_id, Notification.user_id==user.id).first()
    if not n: raise HTTPException(404, "Not found")
    n.is_read = True; db.commit()
    return {"ok": True, "is_read": True}

@router.post("/{notif_id}/unread")
def mark_unread(notif_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id==notif_id, Notification.user_id==user.id).first()
    if not n: raise HTTPException(404, "Not found")
    n.is_read = False; db.commit()
    return {"ok": True, "is_read": False}

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user = Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id==user.id, Notification.is_read==False).update({"is_read": True})
    db.commit()
    return {"ok": True}