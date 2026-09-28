from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post, Comment, Like
from app.routes.auth import get_current_user

router = APIRouter(prefix="/user/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    my_posts = db.query(Post).filter(Post.owner_id == current_user.id).all()
    post_ids = [p.id for p in my_posts]

    total_posts = len(my_posts)
    # Comment model la user_id than iruku ma
    total_comments_made = db.query(Comment).filter(Comment.user_id == current_user.id).count()
    total_likes_received = db.query(Like).filter(Like.post_id.in_(post_ids)).count() if post_ids else 0
    total_views = sum([p.views or 0 for p in my_posts])

    per_post = []
    for p in my_posts:
        per_post.append({
            "title": p.title[:15],
            "likes": db.query(Like).filter(Like.post_id == p.id).count(),
            "comments": db.query(Comment).filter(Comment.post_id == p.id).count()
        })

    return {
        "total_posts": total_posts,
        "total_comments_made": total_comments_made,
        "total_likes_received": total_likes_received,
        "total_views": total_views,
        "per_post": per_post
    }