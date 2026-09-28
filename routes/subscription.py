from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.routes.auth import get_current_user  # inga fix panniten ma
from app.routes.notifications import create_notification

router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.post("/seed-plans")
def seed_plans(db: Session = Depends(get_db)):
    default_plans = [
        {"name": "Free", "price": 0},
        {"name": "Pro", "price": 199},
        {"name": "Premium", "price": 499},
    ]
    created = []
    for p in default_plans:
        existing = db.query(models.Plan).filter(models.Plan.name == p["name"]).first()
        if not existing:
            new_plan = models.Plan(name=p["name"], price=p["price"])
            db.add(new_plan)
            created.append(p["name"])
    db.commit()
    return {"msg": "Plans seeded", "created": created}

@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    return db.query(models.Plan).all()

@router.post("/subscribe/{plan_id}")
def subscribe(plan_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    old_subs = db.query(models.Subscription).filter(models.Subscription.user_id == current_user.id, models.Subscription.is_active == True).all()
    for s in old_subs:
        s.is_active = False

    new_sub = models.Subscription(user_id=current_user.id, plan_id=plan_id, is_active=True)
    db.add(new_sub)

    history = models.BillingHistory(user_id=current_user.id, plan_id=plan_id, amount=plan.price)
    db.add(history)
    db.commit()
    db.refresh(new_sub)

    # Bell notification
    create_notification(
        db,
        current_user.id,
        f"Your subscription to {plan.name} (₹{plan.price}) is activated!",
        "subscription"
    )

    return {"msg": f"Subscribed to {plan.name}", "subscription": new_sub}

@router.get("/my-plan")
def my_plan(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.user_id == current_user.id, models.Subscription.is_active == True).first()
    if not sub:
        return {"plan": "Free", "msg": "No active subscription"}
    plan = db.query(models.Plan).filter(models.Plan.id == sub.plan_id).first()
    return {"subscription": sub, "plan": plan}

@router.get("/my-history")
def my_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.BillingHistory).filter(models.BillingHistory.user_id == current_user.id).order_by(models.BillingHistory.created_at.desc()).all()