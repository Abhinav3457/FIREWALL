from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AttackLog(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    method: Mapped[str] = mapped_column(String(12), nullable=False)
    path: Mapped[str] = mapped_column(String(300), nullable=False)
    ip: Mapped[str] = mapped_column(String(80), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(300), default="unknown")
    payload_snippet: Mapped[str] = mapped_column(Text, default="")
    matched_rule: Mapped[str] = mapped_column(String(150), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    action: Mapped[str] = mapped_column(String(20), default="blocked")
