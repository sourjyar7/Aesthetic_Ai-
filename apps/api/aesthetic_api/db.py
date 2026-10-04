"""Database engine. One engine per process, created on first use."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from aesthetic_api.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_settings().database_url,
        # Neon suspends idle computes and drops their connections; test each
        # pooled connection before use and replace it if it has gone stale.
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
