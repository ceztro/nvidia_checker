import os
import smtplib
from email.message import EmailMessage

def send_email(subject: str, body: str):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    mail_to = os.environ["MAIL_TO"]
    mail_from = os.environ.get("MAIL_FROM", user)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.send_message(msg)

if __name__ == "__main__":
    subject = os.environ.get("MAIL_SUBJECT", "NVIDIA stock checker")
    body = os.environ.get("MAIL_BODY", "No body provided.")
    send_email(subject, body)