from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from litestar import Litestar, get
from litestar.config.app import AppConfig
from litestar.di import Provide

from src.entrypoint.auth.guards import jwt_auth
from src.entrypoint.auth.handlers import login, register
from src.entrypoint.config import Settings
from src.entrypoint.middleware import RequestLoggingMiddleware
from src.entrypoint.scrum.handlers import ProyectoController


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


async def get_proyecto_repository(settings: Settings) -> object:
    if settings.is_turso_enabled:
        from src.scrum.adapters.proyecto_repo_turso import (
            ProyectoRepositorioTurso,
        )

        return ProyectoRepositorioTurso(settings)
    else:
        from src.scrum.adapters.proyecto_repo_sqlite import (
            ProyectoRepositorySQLite,
        )

        return ProyectoRepositorySQLite()


def _build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
        if not settings.skip_db_init:
            from src.db.connection import init_db

            await init_db(settings)

        if settings.is_turso_enabled:
            from libsql_client import create_client

            from src.scrum.infrastructure.outbox_turso import TursoOutboxClient

            url = settings.turso_url.replace("libsql://", "https://", 1)
            client = create_client(url=url, auth_token=settings.turso_token)
            outbox_client = TursoOutboxClient(client)
        else:
            import aiosqlite

            from src.scrum.infrastructure.outbox_sqlite import SqliteOutboxClient

            conn = await aiosqlite.connect(settings.sqlite_path)
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA foreign_keys=ON")
            outbox_client = SqliteOutboxClient(conn)

        from src.scrum.infrastructure.outbox_handlers import (
            LoggingHandler,
            ProjectionHandler,
            WebhookHandler,
        )
        from src.scrum.infrastructure.outbox_worker import OutboxWorker

        handlers: list = [LoggingHandler()]
        if settings.outbox_webhook_url:
            handlers.append(WebhookHandler(settings.outbox_webhook_url))
        if not settings.is_turso_enabled:
            handlers.append(ProjectionHandler(conn))

        worker = OutboxWorker(outbox_client, handlers=handlers)
        await worker.start()
        try:
            yield
        finally:
            await worker.stop()
            if settings.is_turso_enabled:
                await client.close()
            else:
                await conn.close()

    return lifespan


def _on_app_init(app_config: AppConfig) -> AppConfig:
    env_file = str(Path(__file__).parents[3] / ".env")
    settings = Settings.from_env(env_file)
    app_config.dependencies["settings"] = Provide(lambda: settings, use_cache=True, sync_to_thread=False)
    app_config.dependencies["proyecto_repo"] = Provide(get_proyecto_repository, use_cache=True)

    from src.idp.adapters.usuario_repo_sqlite import (
        UsuarioRepositorySQLite,
    )

    app_config.dependencies["usuario_repo"] = Provide(lambda: UsuarioRepositorySQLite(), use_cache=False, sync_to_thread=False)
    app_config.lifespan.append(_build_lifespan(settings))
    return app_config


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            health,
            login,
            register,
            ProyectoController,
        ],
        on_app_init=[_on_app_init, jwt_auth.on_app_init],
        middleware=[RequestLoggingMiddleware],
    )
