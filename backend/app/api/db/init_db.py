from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.rule import Rule
from app.models.user import User

DEFAULT_RULES = [
    {
        "name": "SQL Injection",
        "pattern": r"(?i)(union\s+select|or\s+1=1|drop\s+table|sleep\()",
        "description": "Detect common SQL injection payloads",
        "severity": "high",
    },
    {
        "name": "XSS",
        "pattern": r"(?i)(<script|javascript:|onerror=|onload=)",
        "description": "Detect reflected and stored XSS attempts",
        "severity": "high",
    },
    {
        "name": "Command Injection",
        "pattern": r"(?i)(;\s*(cat|ls|wget|curl)|\|\||&&)",
        "description": "Detect command injection syntax",
        "severity": "critical",
    },
    {
        "name": "Path Traversal",
        "pattern": r"(\.\./|%2e%2e%2f)",
        "description": "Detect path traversal payloads",
        "severity": "medium",
    },
]


def seed_database(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == settings.admin_email))
    if not admin:
        db.add(
            User(
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                is_active=True,
                otp_enabled=True,
            )
        )

    for rule_data in DEFAULT_RULES:
        exists = db.scalar(select(Rule).where(Rule.name == rule_data["name"]))
        if not exists:
            db.add(Rule(**rule_data, enabled=True))

    db.commit()
