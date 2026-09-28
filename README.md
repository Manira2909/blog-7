# Blog Premium API

FastAPI Blog API with JWT Auth, Posts, Likes/Comments, and Email Notifications.

## Setup
1. Clone repo
2. Create virtual env: `python -m venv venv` then `venv\Scripts\activate` (Windows)
3. Install: `pip install -r requirements.txt`
4. Create `.env` file in root:
5. Run: `python -m uvicorn app.main:app --reload`
6. Docs: http://127.0.0.1:8000/docs

## Features
- **Auth:** POST /auth/register, POST /auth/direct-login, GET /auth/me (JWT)
- **Posts:** POST /posts, GET /posts, GET /posts/{id}, DELETE /posts/{id}
- **Interactions:** POST /posts/{id}/like, POST /posts/{id}/comment
- **Email Notifications:** Mailtrap SMTP via BackgroundTasks on Like/Comment. Includes Post Title, User, Activity.

## Proof
Mailtrap inbox screenshot shows "Test from Blog API" received successfully.