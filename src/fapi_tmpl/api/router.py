"""HTTP routes exposed by the FastAPI template."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "ok"}
