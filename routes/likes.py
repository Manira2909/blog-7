from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Like, Post, User
from ..auth import get_current_user
from .notifications import create_notification

router = APIRouter(prefix="/likes", tags=["Likes"])

@router.post("/post/{post_id}")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found ma")

    existing = db.query(Like).filter(
        Like.post_id == post_id,
        Like.owner_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already liked ma")

    new_like = Like(post_id=post_id, owner_id=current_user.id)
    db.add(new_like)
    db.commit()

    # Notification trigger - post owner ku like alert
    # thanakuthane like panna notification venda
    post_owner_id = getattr(post, 'owner_id', getattr(post, 'author_id', None))
    if post_owner_id and post_owner_id != current_user.id:
        create_notification(
            db,
            post_owner_id,
            f"{current_user.username} liked your post",
            "like"
        )

    count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    return {"message": "Liked!", "post_id": post_id, "like_count": count}

@router.delete("/post/{post_id}")
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.owner_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(status_code=404, detail="Like pannala ma")

    db.delete(like)
    db.commit()

    count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    return {"message": "Unliked!", "post_id": post_id, "like_count": count}

@router.get("/post/{post_id}/count")
def get_like_count(post_id: int, db: Session = Depends(get_db)):
    count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    return {"post_id": post_id, "like_count": count}

@router.get("/post/{post_id}/users")
def get_liked_users(post_id: int, db: Session = Depends(get_db)):
    likes = db.query(Like).filter(Like.post_id == post_id).all()
    result = []
    for l in likes:
        user = db.query(User).filter(User.id == l.owner_id).first()
        result.append({
            "user_id": l.owner_id,
            "username": user.username if user else "User"
        })
    return {"post_id": post_id, "liked_by": result, "count": len(result)}