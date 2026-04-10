from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import create_access_token, verify_password
from app.models.login_attempt import LoginAttempt
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse, VerifyOtpRequest
from app.services.email_service import send_otp_email
from app.services.otp_service import create_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["Auth"])


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email))

    if not user or not verify_password(payload.password, user.password_hash):
        login_attempt = LoginAttempt(
            email=payload.email,
            ip=_client_ip(request),
            success=False,
        )
        db.add(login_attempt)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    login_attempt = LoginAttempt(
        email=payload.email,
        ip=_client_ip(request),
        success=True,
    )
    db.add(login_attempt)
    db.commit()

    if not user.otp_enabled:
        return LoginResponse(otp_required=False, message=create_access_token(user.email))

    otp = create_otp(user.email, db)
    send_otp_email(user.email, otp)
    return LoginResponse(otp_required=True, message="OTP sent to your email")


@router.post("/verify-otp", response_model=TokenResponse)
def verify(payload: VerifyOtpRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_otp(payload.email, payload.otp, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)
