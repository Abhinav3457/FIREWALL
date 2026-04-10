from datetime import datetime, timezone

from pymongo.database import Database

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import get_next_sequence

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


def seed_database(db: Database) -> None:
    now = datetime.now(timezone.utc)

    admin = db.users.find_one({"email": settings.admin_email})
    if not admin:
        db.users.insert_one(
            {
                "id": get_next_sequence("users"),
                "email": settings.admin_email,
                "password_hash": hash_password(settings.admin_password),
                "is_active": True,
                "otp_enabled": True,
                "created_at": now,
            }
        )

    for rule_data in DEFAULT_RULES:
        exists = db.rules.find_one({"name": rule_data["name"]})
        if not exists:
            db.rules.insert_one(
                {
                    "id": get_next_sequence("rules"),
                    **rule_data,
                    "enabled": True,
                    "created_at": now,
                }
            )
