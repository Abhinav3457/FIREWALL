from datetime import datetime

from pydantic import BaseModel


class RuleOut(BaseModel):
    id: int
    name: str
    pattern: str
    description: str
    severity: str
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RuleToggleRequest(BaseModel):
    enabled: bool
