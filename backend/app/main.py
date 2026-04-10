import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.db.init_db import seed_database
from app.db.session import engine, Base, SessionLocal
from app.api.routes import auth, dashboard, health, logs, rules
from app.core.config import settings
from app.core.mongo_client import check_mongo_connection
from app.core.redis_client import check_redis_connection
from app.middleware.firewall import FirewallMiddleware

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def startup_event():
    """Initialize database on app startup."""
    logger.info("Environment loaded: %s", settings.environment_summary())
    check_mongo_connection()
    check_redis_connection()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(FirewallMiddleware)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


def _error_payload(
    *,
    status_code: int,
    detail: str,
    request: Request,
    error_code: str,
    extra: object | None = None,
) -> dict:
    request_id = str(uuid4())
    payload = {
        "error": {
            "code": error_code,
            "detail": detail,
            "request_id": request_id,
            "path": request.url.path,
        },
        # Keep this key for existing frontend handling patterns.
        "detail": detail,
    }
    if extra is not None:
        payload["error"]["extra"] = extra
    return payload


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail_text = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            status_code=exc.status_code,
            detail=detail_text,
            request=request,
            error_code="HTTP_ERROR",
            extra=exc.detail if not isinstance(exc.detail, str) else None,
        ),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation error",
            request=request,
            error_code="VALIDATION_ERROR",
            extra=exc.errors(),
        ),
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error on %s", request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            request=request,
            error_code="INTERNAL_SERVER_ERROR",
        ),
    )
