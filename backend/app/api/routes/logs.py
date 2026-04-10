from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.attack_log import AttackLog
from app.schemas.log import PaginatedLogs

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=PaginatedLogs)
def get_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
) -> PaginatedLogs:
    total = db.query(AttackLog).count()
    rows = db.scalars(
        select(AttackLog)
        .order_by(desc(AttackLog.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        {
            "id": row.id,
            "timestamp": row.timestamp,
            "method": row.method,
            "path": row.path,
            "ip": row.ip,
            "user_agent": row.user_agent,
            "payload_snippet": row.payload_snippet,
            "matched_rule": row.matched_rule,
            "severity": row.severity,
            "action": row.action,
        }
        for row in rows
    ]

    return PaginatedLogs(total=total, page=page, page_size=page_size, items=items)
