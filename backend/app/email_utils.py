import random
from email.message import EmailMessage

import aiosmtplib

from app.config import settings


def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


async def send_otp_email(to_email: str, otp: str) -> None:
    if not settings.email_username or not settings.email_password:
        return

    msg = EmailMessage()
    msg["From"] = settings.email_from or settings.email_username
    msg["To"] = to_email
    msg["Subject"] = "Your CAFW verification code"
    msg.set_content(f"Your OTP is: {otp}. It expires in 10 minutes.")

    await aiosmtplib.send(
        msg,
        hostname=settings.email_host,
        port=settings.email_port,
        username=settings.email_username,
        password=settings.email_password,
        start_tls=True,
    )
