import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta

def generate_invoice(user, plan, transaction_id):
    folder = "media/invoices"
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{transaction_id}.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "BLOG PREMIUM - INVOICE")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"User Name: {user.username}")
    c.drawString(100, 680, f"Email: {user.email}")
    c.drawString(100, 660, f"Plan Name: {plan.name}")
    c.drawString(100, 640, f"Price: ${plan.price}")
    c.drawString(100, 620, f"Start Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    c.drawString(100, 600, f"End Date: {(datetime.utcnow()+timedelta(days=30)).strftime('%Y-%m-%d')}")
    c.drawString(100, 580, f"Transaction ID: {transaction_id}")
    c.drawString(100, 540, "Thank you for subscribing! - Blog Premium Team")
    c.save()
    return file_path