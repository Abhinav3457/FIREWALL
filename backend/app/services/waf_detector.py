from __future__ import annotations

from dataclasses import dataclass

from redis.exceptions import RedisError
from starlette.requests import Request

from app.config import settings
from app.redis_client import get_redis_client
from app.services.waf_rules import RuleDefinition


@dataclass(frozen=True)
class AttackMatch:
    attack_type: str
    severity: str
    reason: str
    payload_excerpt: str


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def build_text_sources(request: Request, body_text: str) -> dict[str, str]:
    headers_text = " ".join([
        f"{key}: {value}" for key, value in request.headers.items()
    ])
    return {
        "path": request.url.path,
        "query": request.url.query,
        "headers": headers_text,
        "body": body_text,
        "url": str(request.url),
    }


def check_large_payload(rule: RuleDefinition | None, body_len: int) -> AttackMatch | None:
    if rule is None:
        return None
    if body_len > settings.waf_max_body_bytes:
        reason = f"Payload size {body_len} exceeds limit {settings.waf_max_body_bytes}"
        return AttackMatch(
            attack_type=rule.category,
            severity=rule.severity,
            reason=reason,
            payload_excerpt=reason,
        )
    return None


async def check_bruteforce(rule: RuleDefinition | None, request: Request) -> AttackMatch | None:
    if rule is None:
        return None
    if not request.url.path.endswith("/auth/login"):
        return None

    redis_client = get_redis_client()
    ip_address = get_client_ip(request)
    key = f"waf:login:{ip_address}"
    lock_key = f"waf:login:lock:{ip_address}"
    try:
        locked = await redis_client.ttl(lock_key)
    except RedisError:
        return None

    if locked and locked > 0:
        reason = f"Login temporarily locked for {locked} seconds"
        return AttackMatch(
            attack_type=rule.category,
            severity=rule.severity,
            reason=reason,
            payload_excerpt=reason,
        )

    try:
        attempts = await redis_client.incr(key)
    except RedisError:
        return None

    if attempts == 1:
        try:
            await redis_client.expire(key, settings.waf_login_window_seconds)
        except RedisError:
            return None

    if attempts > settings.waf_login_max_attempts:
        try:
            await redis_client.set(lock_key, "1", ex=settings.waf_login_lock_seconds)
        except RedisError:
            pass
        reason = "Login rate limit exceeded"
        return AttackMatch(
            attack_type=rule.category,
            severity=rule.severity,
            reason=reason,
            payload_excerpt=reason,
        )
    return None


def detect_attack(rules: list[RuleDefinition], sources: dict[str, str]) -> AttackMatch | None:
    lowered = {key: value.lower() for key, value in sources.items()}

    for rule in rules:
        if rule.key in {"large_payload", "brute_force"}:
            continue
        for pattern in rule.patterns:
            for location in rule.locations:
                haystack = lowered.get(location, "")
                if pattern and pattern in haystack:
                    payload_excerpt = " ".join([sources.get("path", ""), sources.get("query", ""), sources.get("body", "")])
                    payload_excerpt = payload_excerpt.strip()[:500]
                    return AttackMatch(
                        attack_type=rule.category,
                        severity=rule.severity,
                        reason=f"Matched pattern: {pattern}",
                        payload_excerpt=payload_excerpt,
                    )
    return None
