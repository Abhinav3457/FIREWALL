from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.database import SessionLocal
from app.models import AttackLog, RequestLog
from app.services.waf_detector import (
    AttackMatch,
    build_text_sources,
    check_bruteforce,
    check_large_payload,
    detect_attack,
    get_client_ip,
)
from app.services.waf_rules import get_enabled_rules


class WAFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        allow_paths = [p.strip() for p in settings.waf_allow_paths.split(",") if p.strip()]
        if any(request.url.path.startswith(path) for path in allow_paths):
            db = SessionLocal()
            try:
                self._store_request(db, request, blocked=False, attack_type=None)
            finally:
                db.close()
            return await call_next(request)
        body = await request.body()
        request._body = body
        body_text = body.decode("utf-8", errors="ignore")
        sources = build_text_sources(request, body_text)

        db = SessionLocal()
        try:
            rules = get_enabled_rules(db)
            rules_by_key = {rule.key: rule for rule in rules}

            large_payload = check_large_payload(rules_by_key.get("large_payload"), len(body))
            if large_payload:
                return self._block_and_log(db, request, large_payload)

            brute_force = await check_bruteforce(rules_by_key.get("brute_force"), request)
            if brute_force:
                return self._block_and_log(db, request, brute_force)

            match = detect_attack(rules, sources)
            if match:
                return self._block_and_log(db, request, match)

            self._store_request(db, request, blocked=False, attack_type=None)
        finally:
            db.close()

        return await call_next(request)

    @staticmethod
    def _store_request(db, request: Request, blocked: bool, attack_type: str | None):
        db.add(
            RequestLog(
                ip_address=get_client_ip(request),
                method=request.method,
                path=request.url.path,
                blocked=blocked,
                attack_type=attack_type,
            )
        )
        db.commit()

    def _block_and_log(self, db, request: Request, match: AttackMatch) -> JSONResponse:
        db.add(
            AttackLog(
                ip_address=get_client_ip(request),
                method=request.method,
                path=request.url.path,
                attack_type=match.attack_type,
                severity=match.severity,
                reason=match.reason,
                payload_excerpt=match.payload_excerpt,
            )
        )
        self._store_request(db, request, blocked=True, attack_type=match.attack_type)
        return JSONResponse(
            status_code=403,
            content={"detail": "Blocked by firewall", "reason": match.reason},
        )
