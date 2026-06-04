from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from src.db.schema import CREATE_TABLES

def _db_path() -> str:
    return os.getenv("SQLITE_PATH", "local.db")


def _turso_url() -> str:
    return os.getenv("TURSO_DATABASE_URL", "")


def _turso_token() -> str:
    return os.getenv("TURSO_AUTH_TOKEN", "")


def is_turso_enabled() -> bool:
    return bool(_turso_url() and _turso_token())


@asynccontextmanager
async def get_sqlite_connection() -> AsyncIterator:
    import aiosqlite

    async with aiosqlite.connect(_db_path()) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        yield conn


@asynccontextmanager
async def get_turso_client() -> AsyncIterator:
    from libsql_client import create_client

    url = _turso_url().replace("libsql://", "https://", 1)
    client = create_client(url=url, auth_token=_turso_token())
    try:
        yield client
    finally:
        await client.close()


async def init_db() -> None:
    if is_turso_enabled():
        async with get_turso_client() as client:
            for stmt in CREATE_TABLES.split(";"):
                stmt = stmt.strip()
                if stmt:
                    await client.execute(stmt)
    else:
        async with get_sqlite_connection() as conn:
            await conn.executescript(CREATE_TABLES)
            await conn.commit()
