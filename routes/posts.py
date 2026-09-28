from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Post, Comment, Like
from app.routes.auth import get_current_user
from app.routes.notifications import create_notification
from datetime import datetime
from typing import Optional
import shutil, os, uuid

router = APIRouter(prefix="/posts", tags=["Posts"])

class CommentIn(BaseModel):
    content: str

@router.post("/")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    action: str = Form("publish_now"),
    scheduled_at: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    image_path = None
    if image:
        os.makedirs("uploads", exist_ok=True)
        fname = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = f"uploads/{fname}"
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    status = "published"
    scheduled_dt = None
    published_at = datetime.now()

    if action == "draft":
        status = "draft"
        scheduled_dt = None
        published_at = None
    elif action == "schedule":
        if not scheduled_at:
            raise HTTPException(400, "scheduled_at required for schedule")
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at)
        except ValueError:
            raise HTTPException(400, "Invalid datetime format. Use YYYY-MM-DDTHH:MM:SS")
        if scheduled_dt <= datetime.now():
            raise HTTPException(400, "scheduled_at must be a future datetime")
        status = "scheduled"
        published_at = None
    else:
        status = "published"
        scheduled_dt = None
        published_at = datetime.now()

    p = Post(title=title, content=content, author_id=user.id, owner_id=user.id,
             image_path=image_path, status=status,
             scheduled_at=scheduled_dt, published_at=published_at)
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.get("/")
def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.status == "published").order_by(Post.created_at.desc()).all()

@router.get("/mine")
def get_my_posts(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(Post).filter(Post.owner_id == user.id).order_by(Post.created_at.desc()).all()

@router.put("/{post_id}")
def update_post(
    post_id: int,
    title: str = Form(None),
    content: str = Form(None),
    action: str = Form(None),
    scheduled_at: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    p = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
    if not p:
        raise HTTPException(404, "Post not found")
    if title: p.title = title
    if content: p.content = content
    if action:
        if action == "draft":
            p.status = "draft"; p.scheduled_at = None; p.published_at = None
        elif action == "schedule":
            if not scheduled_at:
                raise HTTPException(400, "scheduled_at required")
            sdt = datetime.fromisoformat(scheduled_at)
            if sdt <= datetime.now():
                raise HTTPException(400, "scheduled_at must be future datetime")
            p.status = "scheduled"; p.scheduled_at = sdt; p.published_at = None
        elif action == "publish_now":
            p.status = "published"; p.scheduled_at = None; p.published_at = datetime.now()
    db.commit(); db.refresh(p)
    return p

@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if not post: raise HTTPException(404, "Post not found")
    ex = db.query(Like).filter(Like.post_id==post_id, Like.owner_id==user.id).first()
    if ex: db.delete(ex); db.commit(); return {"liked": False}
    db.add(Like(post_id=post_id, owner_id=user.id, user_id=user.id)); db.commit()
    return {"liked": True}

@router.get("/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.post_id==post_id).order_by(Comment.created_at.desc()).all()

@router.post("/{post_id}/comments")
@router.post("/{post_id}/comment")
def add_comment(post_id: int, data: CommentIn, db: Session = Depends(get_db), user = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if not post: raise HTTPException(404, "Post not found")
    c = Comment(content=data.content, user_id=user.id, post_id=post_id)
    db.add(c); db.commit(); db.refresh(c)
    if post.author_id!= user.id:
        create_notification(db, post.author_id, f"{user.username} commented: {data.content[:40]}", "comment")
    return c