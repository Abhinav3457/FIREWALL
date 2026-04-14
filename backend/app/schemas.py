from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginInitiateResponse(BaseModel):
    message: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


class AttackLogItem(BaseModel):
    id: int
    ip_address: str
    method: str
    path: str
    attack_type: str
    severity: str
    reason: str
    payload_excerpt: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    total_attacks_blocked: int
    total_users: int
    verified_users: int
    latest_attacks: list[AttackLogItem]


class AttackLogList(BaseModel):
    items: list[AttackLogItem]


class RuleItem(BaseModel):
    id: int
    key: str
    name: str
    category: str
    severity: str
    enabled: bool
    patterns: list[str]
    locations: list[str]

    model_config = ConfigDict(from_attributes=True)


class RuleToggleRequest(BaseModel):
    key: str
    enabled: bool


class RuleList(BaseModel):
    items: list[RuleItem]


class SecurityStats(BaseModel):
    total_requests: int
    blocked_requests: int
    attack_distribution: dict[str, int]
