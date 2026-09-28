from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os
from dotenv import load_dotenv
load_dotenv()
from app.database import get_db
from app.models import User
from app.routes.auth import create_token # correct import for your structure

router = APIRouter()

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid profile email'},
)

@router.get("/auth/login/google")
async def login_google(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/callback"
    return await oauth.auth0.authorize_redirect(request, redirect_uri, connection="google-oauth2")

@router.get("/auth/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.auth0.authorize_access_token(request)
    userinfo = token.get("userinfo")

    if not userinfo or "email" not in userinfo:
        return RedirectResponse("/?error=no_email")

    username = userinfo.get("nickname") or userinfo["email"].split("@")[0]

    user = db.query(User).filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(
            username=username,
            email=userinfo["email"],
            hashed_password="auth0"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    request.session["user_id"] = user.id
    access_token = create_token(data={"sub": user.username})
    return RedirectResponse(f"/dashboard.html?token={access_token}")

@router.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")