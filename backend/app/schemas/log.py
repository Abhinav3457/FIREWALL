from datetime import datetime

from pydantic import BaseModel


class AttackLogOut(BaseModel):
    id: int
    timestamp: datetime
    method: str
    path: str
    ip: str
    user_agent: str
    payload_snippet: str
    matched_rule: str
    severity: str
    action: str

    model_config = {"from_attributes": True}


class PaginatedLogs(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AttackLogOut]
