import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_db
from app.email_utils import generate_otp, send_otp_email
from app.models import User
from app.redis_client import get_redis_client
from app.schemas import LoginInitiateResponse, LoginRequest, TokenResponse, VerifyOtpRequest
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _otp_key(email: str) -> str:
    return f"otp:{email.lower()}"


def _attempts_key(email: str) -> str:
    return f"otp_attempts:{email.lower()}"


def _lock_key(email: str) -> str:
    return f"otp_lock:{email.lower()}"


def _hash_otp(email: str, otp: str) -> str:
    return hashlib.sha256(f"{email.lower()}:{otp}:{settings.secret_key}".encode("utf-8")).hexdigest()


async def _assert_not_locked(redis_client: Redis, email: str) -> None:
    try:
        lock_ttl = await redis_client.ttl(_lock_key(email))
    except RedisError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc

    if lock_ttl and lock_ttl > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many invalid OTP attempts. Try again in {lock_ttl} seconds.",
        )


@router.post("/register", response_model=LoginInitiateResponse)
def register_disabled():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Public signup is disabled. Only the pre-registered admin account is allowed.",
    )


@router.post("/login", response_model=LoginInitiateResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    admin_email = settings.admin_email.lower().strip()
    email = payload.email.lower().strip()

    if email != admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    redis_client = get_redis_client()
    await _assert_not_locked(redis_client, email)

    otp = generate_otp()
    hashed_otp = _hash_otp(email, otp)

    try:
        await redis_client.set(_otp_key(email), hashed_otp, ex=settings.otp_expire_seconds)
        await redis_client.delete(_attempts_key(email))
    except RedisError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc

    try:
        await send_otp_email(email, otp)
    except Exception:
        await redis_client.delete(_otp_key(email))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OTP email delivery failed")

    return LoginInitiateResponse(message="OTP sent to your email. It expires in 5 minutes.")


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    admin_email = settings.admin_email.lower().strip()

    if email != admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP flow")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP flow")

    redis_client = get_redis_client()
    await _assert_not_locked(redis_client, email)

    try:
        stored_hash = await redis_client.get(_otp_key(email))
    except RedisError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc

    if not stored_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired or not requested")

    incoming_hash = _hash_otp(email, payload.otp)
    if incoming_hash != stored_hash:
        try:
            attempts = await redis_client.incr(_attempts_key(email))
            ttl = await redis_client.ttl(_otp_key(email))
        except RedisError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc

        if ttl and ttl > 0:
            try:
                await redis_client.expire(_attempts_key(email), ttl)
            except RedisError as exc:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc

        if attempts >= settings.otp_max_attempts:
            try:
                await redis_client.set(_lock_key(email), "1", ex=settings.otp_lock_seconds)
                await redis_client.delete(_otp_key(email))
                await redis_client.delete(_attempts_key(email))
            except RedisError as exc:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many invalid OTP attempts. Locked for {settings.otp_lock_seconds} seconds.",
            )

        remaining = settings.otp_max_attempts - attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining} attempt(s) remaining.",
        )

    try:
        await redis_client.delete(_otp_key(email))
        await redis_client.delete(_attempts_key(email))
    except RedisError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OTP service unavailable") from exc

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
