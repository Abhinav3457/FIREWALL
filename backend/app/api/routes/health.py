from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "CAFW backend is running", "health": "/health", "docs": "/docs"}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
