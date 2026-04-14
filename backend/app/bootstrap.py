from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.services.waf_rules import ensure_default_rules
from app.security import hash_password


def ensure_admin_user(db: Session) -> None:
    if not settings.admin_email:
        raise RuntimeError("ADMIN_EMAIL must be configured")

    password_hash = settings.admin_password_hash
    if not password_hash and settings.admin_password:
        password_hash = hash_password(settings.admin_password)

    if not password_hash:
        raise RuntimeError("Set ADMIN_PASSWORD_HASH or ADMIN_PASSWORD")

    admin_email = settings.admin_email.lower().strip()
    user = db.query(User).filter(User.email == admin_email).first()

    if user is None:
        user = User(
            email=admin_email,
            password_hash=password_hash,
            is_verified=True,
        )
        db.add(user)
    else:
        user.password_hash = password_hash
        user.is_verified = True

    db.commit()


def ensure_security_rules(db: Session) -> None:
    _ensure_attack_log_columns(db)
    ensure_default_rules(db)


def _ensure_attack_log_columns(db: Session) -> None:
    inspector = inspect(db.get_bind())
    try:
        columns = {col["name"] for col in inspector.get_columns("attack_logs")}
    except Exception:
        return

    if "attack_type" not in columns:
        db.execute(text("ALTER TABLE attack_logs ADD COLUMN attack_type VARCHAR(64) NOT NULL DEFAULT 'Unknown'"))
    if "severity" not in columns:
        db.execute(text("ALTER TABLE attack_logs ADD COLUMN severity VARCHAR(16) NOT NULL DEFAULT 'Low'"))
    db.commit()
