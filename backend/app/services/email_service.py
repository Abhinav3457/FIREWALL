import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_otp_email(to_email: str, otp: str) -> None:
    if not settings.smtp_enabled:
        # In development, disable SMTP and print code to server logs.
        print(f"[CAFW][OTP] {to_email}: {otp}")
        return

    msg = EmailMessage()
    msg["Subject"] = "Your CAFW OTP Code"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(f"Your OTP code is: {otp}. It will expire in 5 minutes.")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_pass)
        smtp.send_message(msg)
