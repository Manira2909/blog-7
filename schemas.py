from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User ku ma
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Post ku ma
class PostCreate(BaseModel):
    title: str
    content: str

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    image_path: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    content: str
    author_id: int
    post_id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# Token ku ma
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Subscription Plans ku ma (NEW)
class PlanOut(BaseModel):
    id: int
    name: str
    price: float
    max_posts: int
    max_images_per_post: int
    max_likes_per_day: int
    max_comments_per_day: int
    class Config:
        from_attributes = True

class BillingOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    transaction_id: str
    amount: float
    start_date: datetime
    end_date: datetime
    invoice_path: str
    class Config:
        from_attributes = True