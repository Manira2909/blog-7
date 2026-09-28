import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MAILTRAP_HOST = os.getenv("MAILTRAP_HOST")
MAILTRAP_PORT = int(os.getenv("MAILTRAP_PORT", 2525))
MAILTRAP_USER = os.getenv("MAILTRAP_USER")
MAILTRAP_PASS = os.getenv("MAILTRAP_PASS")

def send_mail(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = "Blog API <no-reply@blog.com>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT) as server:
        server.starttls()
        server.login(MAILTRAP_USER, MAILTRAP_PASS)
        server.send_message(msg)
    print(f"Mail sent to {to_email}")

def send_like_notification(post_title: str, liker_name: str, owner_email: str):
    time_now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    subject = "Test from Blog API"
    body = f"Hello\n\nNew Like on: {post_title}\nUser: {liker_name}\nActivity: Like\nTime: {time_now}"
    send_mail(owner_email, subject, body)

def send_comment_notification(post_title: str, commenter_name: str, comment_text: str, owner_email: str):
    time_now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    subject = "Test from Blog API"
    body = f"Hello\n\nNew comment on: {post_title}\nUser: {commenter_name}\nComment: {comment_text}\nActivity: Comment\nTime: {time_now}"
    send_mail(owner_email, subject, body)

# aliases for posts.py import - DO NOT DELETE
def notify_like(post_title: str, liker_name: str, owner_email: str):
    return send_like_notification(post_title, liker_name, owner_email)

def notify_comment(post_title: str, commenter_name: str, comment_text: str, owner_email: str):
    return send_comment_notification(post_title, commenter_name, comment_text, owner_email)