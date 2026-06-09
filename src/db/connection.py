from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from src.db.schema import CREATE_TABLES
from src.entrypoint.config import Settings


def _get_settings(settings: Settings | None = None) -> Settings:
    return settings if settings is not None else Settings.from_env()


def is_turso_enabled(settings: Settings | None = None) -> bool:
    return _get_settings(settings).is_turso_enabled


@asynccontextmanager
async def get_sqlite_connection(settings: Settings | None = None) -> AsyncIterator:
    import aiosqlite

    s = _get_settings(settings)
    async with aiosqlite.connect(s.sqlite_path) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        yield conn


@asynccontextmanager
async def get_turso_client(settings: Settings | None = None) -> AsyncIterator:
    from libsql_client import create_client

    s = _get_settings(settings)
    url = s.turso_url.replace("libsql://", "https://", 1)
    client = create_client(url=url, auth_token=s.turso_token)
    try:
        yield client
    finally:
        await client.close()


async def init_db(settings: Settings | None = None) -> None:
    s = _get_settings(settings)
    if s.is_turso_enabled:
        async with get_turso_client(settings) as client:
            for stmt in CREATE_TABLES.split(";"):
                stmt = stmt.strip()
                if stmt:
                    await client.execute(stmt)
    else:
        async with get_sqlite_connection(settings) as conn:
            await conn.executescript(CREATE_TABLES)
            await conn.commit()
