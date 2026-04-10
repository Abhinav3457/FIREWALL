import random
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.core.redis_client import redis_client
from app.core.security import hash_password, verify_password
from app.models.otp_code import OtpCode
from sqlalchemy import select

OTP_TTL_SECONDS = 300
_otp_fallback_store: dict[str, tuple[str, float]] = {}


def _set_otp_cache(key: str, value: str, ttl_seconds: int) -> None:
    try:
        redis_client.setex(key, ttl_seconds, value)
    except RedisError:
        _otp_fallback_store[key] = (value, time.time() + ttl_seconds)


def _get_otp_cache(key: str) -> str | None:
    try:
        return redis_client.get(key)
    except RedisError:
        cached = _otp_fallback_store.get(key)
        if not cached:
            return None
        value, expires_at = cached
        if time.time() > expires_at:
            _otp_fallback_store.pop(key, None)
            return None
        return value


def _delete_otp_cache(key: str) -> None:
    try:
        redis_client.delete(key)
    except RedisError:
        _otp_fallback_store.pop(key, None)


def create_otp(email: str, db: Session) -> str:
    code = f"{random.randint(0, 999999):06d}"
    code_hash = hash_password(code)

    cache_key = f"otp:{email}"
    _set_otp_cache(cache_key, code_hash, OTP_TTL_SECONDS)

    otp_code = OtpCode(
        email=email,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=OTP_TTL_SECONDS),
        verified=False,
    )
    db.add(otp_code)
    db.commit()
    return code


def verify_otp(email: str, otp: str, db: Session) -> bool:
    cache_key = f"otp:{email}"
    cached_hash = _get_otp_cache(cache_key)
    if not cached_hash or not verify_password(otp, cached_hash):
        return False

    otp_codes = db.scalars(
        select(OtpCode).where((OtpCode.email == email) & (OtpCode.verified == False))
    ).all()
    for otp_code in otp_codes:
        otp_code.verified = True
    db.commit()

    _delete_otp_cache(cache_key)
    return True
