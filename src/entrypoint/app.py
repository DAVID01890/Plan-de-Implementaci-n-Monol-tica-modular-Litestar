from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from litestar import Litestar, get

from src.entrypoint.scrum.handlers import (
    add_historia,
    add_historia_to_sprint,
    create_proyecto,
    create_sprint,
    delete_proyecto,
    get_proyecto,
    list_proyectos,
    start_sprint,
)


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


async def get_proyecto_repository():
    from src.db.connection import is_turso_enabled

    if is_turso_enabled():
        from src.scrum.adapters.proyecto_repo_turso import (
            ProyectoRepositorioTurso,
        )

        return ProyectoRepositorioTurso()
    else:
        from src.scrum.adapters.proyecto_repo_sqlite import (
            ProyectoRepositorySQLite,
        )

        return ProyectoRepositorySQLite()


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    if os.getenv("SKIP_DB_INIT") != "1":
        from src.db.connection import init_db

        await init_db()

    from src.db.connection import _db_path, _turso_url, _turso_token, is_turso_enabled

    if is_turso_enabled():
        from libsql_client import create_client

        from src.scrum.infrastructure.outbox_turso import TursoOutboxClient

        url = _turso_url().replace("libsql://", "https://", 1)
        client = create_client(url=url, auth_token=_turso_token())
        outbox_client = TursoOutboxClient(client)
    else:
        import aiosqlite

        from src.scrum.infrastructure.outbox_sqlite import SqliteOutboxClient

        conn = await aiosqlite.connect(_db_path())
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        outbox_client = SqliteOutboxClient(conn)

    from src.scrum.infrastructure.outbox_worker import OutboxWorker

    worker = OutboxWorker(outbox_client)
    await worker.start()
    try:
        yield
    finally:
        await worker.stop()
        if is_turso_enabled():
            await client.close()
        else:
            await conn.close()


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            health,
            create_proyecto,
            list_proyectos,
            get_proyecto,
            delete_proyecto,
            add_historia,
            create_sprint,
            add_historia_to_sprint,
            start_sprint,
        ],
        dependencies={
            "proyecto_repo": get_proyecto_repository,
        },
        lifespan=[lifespan],
    )
