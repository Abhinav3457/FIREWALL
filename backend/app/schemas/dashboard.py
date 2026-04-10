from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_attacks: int
    blocked_last_24h: int
    high_severity_last_24h: int
    active_rules: int


class AttackTrendItem(BaseModel):
    hour: str
    attacks: int


class SeverityBreakdownItem(BaseModel):
    severity: str
    count: int
