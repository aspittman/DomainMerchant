import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_TO_EMAIL = os.getenv("ALERT_TO_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Domain Bot")


def send_email_alert(subject: str, body: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("Missing SMTP_USER or SMTP_PASSWORD")

    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"] = ALERT_TO_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)