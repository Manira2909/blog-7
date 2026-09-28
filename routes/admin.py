from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from..database import get_db
from..models import User, Subscription, BillingHistory, Plan, Post

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []

    for user in users:
        sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        ).first()
        bills = db.query(BillingHistory).filter(
            BillingHistory.user_id == user.id
        ).order_by(BillingHistory.created_at.desc()).all()
        post_count = db.query(func.count(Post.id)).filter(Post.owner_id == user.id).scalar() or 0

        validation_status = "OK ✅"
        current_plan_name = "No Plan"
        plan_price = "-"
        billing_start = "-"
        billing_end = "-"

        if sub and sub.plan:
            current_plan_name = sub.plan.name
            plan_price = f"₹{sub.plan.price}"
            max_p = getattr(sub.plan, "max_posts", 10) or 10
            if post_count >= max_p:
                validation_status = f"LIMIT EXCEEDED ❌ - {post_count}/{max_p} posts"
            # start_date iruntha mattum edu
            sd = getattr(sub, "start_date", None)
            ed = getattr(sub, "end_date", None)
            if sd:
                billing_start = sd.strftime("%Y-%m-%d %H:%M")
            else:
                billing_start = sub.created_at.strftime("%Y-%m-%d %H:%M") if sub.created_at else "-"
            if ed:
                billing_end = ed.strftime("%Y-%m-%d %H:%M")

        result.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "current_plan": current_plan_name,
            "plan_price": plan_price,
            "billing_start": billing_start,
            "billing_end": billing_end,
            "last_billing_date": bills[0].created_at.strftime("%Y-%m-%d %H:%M") if bills and bills[0].created_at else "-",
            "last_transaction_id": getattr(bills[0], "transaction_id", "-") if bills else "-",
            "total_posts": post_count,
            "validation_message": validation_status,
            "all_invoices": [{
                "date": b.created_at.strftime("%Y-%m-%d") if b.created_at else "-",
                "amount": b.amount,
                "txn": getattr(b, "transaction_id", "-") or "-",
                "pdf": getattr(b, "invoice_path", "-") or "-"
            } for b in bills]
        })
    return result

@router.get("/exceeded-users")
def exceeded_users_list(db: Session = Depends(get_db)):
    all_users = admin_dashboard(db)
    exceeded = [u for u in all_users if "EXCEEDED" in u['validation_message']]
    return {"count": len(exceeded), "exceeded_users": exceeded}

@router.post("/send-email/{user_id}")
def send_email_notification(user_id: int, message: str, db: Session = Depends(get_db)):
    from.notifications import create_notification
    create_notification(db, user_id, f"📧 Email from Admin: {message}", "email")
    return {"ok": True, "msg": f"Email sent to {user_id}"}

@router.delete("/delete-post/{post_id}")
def delete_post_admin(post_id: int, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if p:
        db.delete(p); db.commit()
    return {"ok": True}