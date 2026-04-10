import smtplib
import logging
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def send_otp_email(to_email: str, otp: str) -> None:
    if not settings.smtp_enabled:
        # In development, disable SMTP and print code to server logs.
        logger.info("SMTP disabled; OTP generated for %s", to_email)
        print(f"[CAFW][OTP] {to_email}: {otp}")
        return

    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_pass:
        logger.error("SMTP is enabled but credentials are incomplete")
        raise RuntimeError("SMTP configuration incomplete")

    msg = EmailMessage()
    msg["Subject"] = "Your CAFW OTP Code"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(f"Your OTP code is: {otp}. It will expire in 5 minutes.")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            smtp.ehlo()
            if settings.smtp_port == 587:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(settings.smtp_user, settings.smtp_pass)
            smtp.send_message(msg)
        logger.info("SMTP email sent successfully to %s", to_email)
    except Exception:
        logger.exception("SMTP email sending failed for %s", to_email)
        raise
