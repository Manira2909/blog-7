from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import re

from app.database import get_db
from app.models import ChatLog, User
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/ai-support", tags=["AI Support"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

def get_ai_reply(message: str) -> str:
    m = message.lower()

    if re.search(r'create.*post|how.*post|new post', m):
        return "To create a post: Log in, click 'New Post' on the Home page, add title and content, upload an image if needed, then click Publish."
    if re.search(r'edit.*post|update.*post', m):
        return "To edit a post: Go to Dashboard, find your post in the list, and click the Edit button. You can only edit your own posts."
    if re.search(r'delete.*post|remove.*post', m):
        return "To delete a post: Go to Dashboard, find your post, and click Delete. This action cannot be undone."
    if re.search(r'subscri|plan|premium|upgrade', m):
        return "Subscription plans: Free (5 posts/day), Basic $1.99 (50 posts/day), Pro $4.99 (200 posts/day), Enterprise $9.99 (unlimited). Go to your Profile page to subscribe."
    if re.search(r'bill|invoice|payment|refund|charge', m):
        return "Billing: An invoice PDF is auto-generated after each payment. You can download invoices from the Admin panel. For refunds, please contact support."
    if re.search(r'profile|password|account|settings', m):
        return "Profile management: Click Profile in the top menu. There you can update your name, bio, and change your password."
    if re.search(r'dashboard|analytic|stat|view|like', m):
        return "Dashboard analytics shows: total posts, comments made, likes received, and total views. The bar chart compares likes vs comments per post."
    if re.search(r'comment|like', m):
        return "To like or comment: Open any post and use the Like button or comment box below the post. You need to be logged in."
    if re.search(r'\bhi\b|hello|hey', m):
        return "Hello! I am your Blog assistant. Ask me about creating posts, subscriptions, billing, dashboard, or profile settings."
    if re.search(r'thank', m):
        return "You are welcome! Do you need any other help?"
    if re.search(r'notification', m):
        return "Notifications: Click the bell icon in the dashboard navbar to see likes, comments, and subscription alerts."

    return "I did not understand that. I can help with: creating posts, editing posts, subscriptions, billing, dashboard analytics, profile management."

@router.post("/", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reply = get_ai_reply(req.message)
    log = ChatLog(
        user_id=current_user.id,
        question=req.message,
        ai_response=reply,
        created_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    return {"reply": reply}

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = db.query(ChatLog).filter(
        ChatLog.user_id == current_user.id
    ).order_by(ChatLog.created_at.desc()).limit(20).all()

    return [
        {"question": l.question, "answer": l.ai_response, "at": l.created_at}
        for l in logs
    ]