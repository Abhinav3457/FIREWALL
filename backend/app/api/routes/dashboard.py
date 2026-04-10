from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.attack_log import AttackLog
from app.models.rule import Rule
from app.schemas.dashboard import AttackTrendItem, DashboardOverview, SeverityBreakdownItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(db: Session = Depends(get_db), _: dict = Depends(get_current_user)) -> DashboardOverview:
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    total_attacks = db.query(AttackLog).count()
    blocked_last_24h = db.query(AttackLog).filter(AttackLog.timestamp >= since).count()
    high_severity_last_24h = db.query(AttackLog).filter(
        and_(AttackLog.timestamp >= since, AttackLog.severity.in_(["high", "critical"]))
    ).count()
    active_rules = db.query(Rule).filter(Rule.enabled == True).count()

    return DashboardOverview(
        total_attacks=total_attacks,
        blocked_last_24h=blocked_last_24h,
        high_severity_last_24h=high_severity_last_24h,
        active_rules=active_rules,
    )


@router.get("/trend", response_model=list[AttackTrendItem])
def trend(db: Session = Depends(get_db), _: dict = Depends(get_current_user)) -> list[AttackTrendItem]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    logs = db.scalars(
        select(AttackLog).filter(AttackLog.timestamp >= since)
    ).all()

    buckets: dict[str, int] = {}
    for log in logs:
        if log.timestamp:
            hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
            buckets[hour_key] = buckets.get(hour_key, 0) + 1

    return [AttackTrendItem(hour=hour, attacks=count) for hour, count in sorted(buckets.items())]


@router.get("/severity", response_model=list[SeverityBreakdownItem])
def severity(db: Session = Depends(get_db), _: dict = Depends(get_current_user)) -> list[SeverityBreakdownItem]:
    rows = db.query(
        AttackLog.severity,
        func.count(AttackLog.id).label("count")
    ).group_by(AttackLog.severity).order_by(desc("count")).all()

    return [SeverityBreakdownItem(severity=row[0] or "unknown", count=int(row[1])) for row in rows]
