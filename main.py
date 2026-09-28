from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import engine, Base, SessionLocal
from app import models
from app.routes import auth, posts, subscription, admin, notifications
from app import dashboard
from app.routes import ai_support
from starlette.middleware.sessions import SessionMiddleware
from app.routes import auth0_auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API with Subscription")
app.add_middleware(SessionMiddleware, secret_key="blog-secret-key-123")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("invoices", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/invoices", StaticFiles(directory="invoices"), name="invoices")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(subscription.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)
app.include_router(ai_support.router)
app.include_router(auth0_auth.router)

# --- Scheduled Publishing: auto-publish job ---
def publish_scheduled_posts():
    db = SessionLocal()
    try:
        now = datetime.now()
        due_posts = db.query(models.Post).filter(
            models.Post.status == "scheduled",
            models.Post.scheduled_at <= now
        ).all()
        for p in due_posts:
            p.status = "published"
            p.published_at = now
            # Author ku notification
            notif = models.Notification(
                user_id=p.owner_id,
                message=f"Your scheduled post '{p.title}' is now published!",
                type="post_published"
            )
            db.add(notif)
            print(f"Published: {p.title}")
        if due_posts:
            db.commit()
    except Exception as e:
        print("Scheduler error:", e)
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(publish_scheduled_posts, 'interval', minutes=1)
scheduler.start()
# --- end scheduler ---

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/dashboard.html")
def serve_dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/admin.html")
def serve_admin():
    return FileResponse("static/admin.html")

@app.get("/api")
def api_root():
    return {"message": "Blog API running ma!"}

@app.get("/health")
def health():
    return {"status": "ok"}