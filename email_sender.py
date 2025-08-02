import smtplib
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(recipient, subject, body):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return "Sender email or password not set in environment variables."

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(SENDER_EMAIL, recipient, message)
        return True
    except Exception as e:
        return str(e)

def send_email_custom(sender_email, sender_password, recipient, subject, body):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, recipient, message)
        return True
    except Exception as e:
        return str(e)
