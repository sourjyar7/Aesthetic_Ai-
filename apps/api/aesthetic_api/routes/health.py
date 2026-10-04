"""Liveness (`/health`) and readiness (`/health/ready`) checks."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from aesthetic_api.db import get_engine

router = APIRouter(prefix="/api/health", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("")
def health() -> dict[str, str]:
    """The process is up. Never touches the database."""
    return {"status": "ok"}


@router.get("/ready", response_model=None)
def ready() -> dict[str, str] | JSONResponse:
    """The service can do real work: the database answers and pgvector is installed."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("select 1"))
            postgres = conn.execute(text("select current_setting('server_version')")).scalar_one()
            pgvector = conn.execute(
                text("select extversion from pg_extension where extname = 'vector'")
            ).scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.warning("readiness check failed: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "reason": "database unreachable"}
        )
    if pgvector is None:
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "reason": "pgvector not installed"}
        )
    return {"status": "ready", "postgres": str(postgres).split()[0], "pgvector": str(pgvector)}
