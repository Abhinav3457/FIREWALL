from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import SessionLocal
from app.models.attack_log import AttackLog
from app.services.detector import detect_attack


async def read_request_payload(request: Request) -> str:
    body = await request.body()

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive

    parts = [request.method, request.url.path, request.url.query]

    if body:
        try:
            parts.append(body.decode("utf-8", errors="ignore"))
        except Exception:
            parts.append(str(body))

    headers = {k.lower(): v for k, v in request.headers.items()}
    parts.append(json.dumps(headers))

    return " | ".join(parts)


class FirewallMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)

        payload = await read_request_payload(request)
        db = SessionLocal()
        try:
            detection = detect_attack(payload, db)
            if detection.matched:
                log = AttackLog(
                    timestamp=datetime.now(timezone.utc),
                    method=request.method,
                    path=request.url.path,
                    ip=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent", "unknown"),
                    payload_snippet=payload[:2000],
                    matched_rule=detection.rule_name,
                    severity=detection.severity,
                    action="blocked",
                )
                db.add(log)
                db.commit()

                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Request blocked by CAFW firewall",
                        "rule": detection.rule_name,
                        "severity": detection.severity,
                    },
                )
        finally:
            db.close()

        return await call_next(request)
