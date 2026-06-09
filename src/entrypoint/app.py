from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from litestar import Litestar, get
from litestar.config.app import AppConfig
from litestar.config.cors import CORSConfig
from litestar.di import Provide

from src.entrypoint.auth.guards import jwt_auth
from src.entrypoint.auth.handlers import login, register
from src.entrypoint.config import Settings
from src.entrypoint.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from src.entrypoint.scrum.handlers import ProyectoController


@get("/health")
async def health(settings: Settings) -> dict[str, str]:
    try:
        if settings.is_turso_enabled:
            from libsql_client import create_client
            url = settings.turso_url.replace("libsql://", "https://", 1)
            client = create_client(url=url, auth_token=settings.turso_token)
            await client.execute("SELECT 1")
            await client.close()
        else:
            from src.db.pool import get_pool as _get_pool
            pool = await _get_pool(settings)
            async with pool.connection() as conn:
                await conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": str(e)}


@get("/debug/profile", exclude_from_auth=True)
async def profile() -> dict[str, object]:
    from src.db.pool import _pool_instance
    from src.scrum.adapters.proyecto_repo_sqlite import _proyecto_list_cache
    from src.entrypoint.auth.guards import _user_cache

    pool_stats: dict[str, object] = {"enabled": False}
    if _pool_instance is not None:
        pool_stats = {
            "enabled": True,
            "size": _pool_instance.size,
            "max_size": _pool_instance.max_size,
            "path": _pool_instance.path,
        }

    return {
        "pool": pool_stats,
        "cache": {
            "proyecto_list": _proyecto_list_cache.stats(),
            "user_cache": _user_cache.stats(),
        },
    }


async def get_proyecto_repository(settings: Settings, pool: object) -> object:
    if settings.is_turso_enabled:
        from src.scrum.adapters.proyecto_repo_turso import (
            ProyectoRepositorioTurso,
        )
        return ProyectoRepositorioTurso(settings)
    else:
        from src.scrum.adapters.proyecto_repo_sqlite import (
            ProyectoRepositorySQLite,
        )
        return ProyectoRepositorySQLite(pool=pool)


async def get_pool_dependency(settings: Settings) -> object:
    if settings.is_turso_enabled:
        return None
    from src.db.pool import get_pool as _get_pool
    return await _get_pool(settings)


async def get_usuario_repo(pool: object, settings: Settings) -> object:
    if settings.is_turso_enabled:
        from src.idp.adapters.usuario_repo_turso import (
            UsuarioRepositorioTurso,
        )
        return UsuarioRepositorioTurso(settings)
    else:
        from src.idp.adapters.usuario_repo_sqlite import (
            UsuarioRepositorySQLite,
        )
        return UsuarioRepositorySQLite(pool=pool)


def _build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
        if not settings.skip_db_init:
            from src.db.connection import init_db
            await init_db(settings)

        pool = None
        if not settings.is_turso_enabled:
            from src.db.pool import get_pool as _get_pool
            pool = await _get_pool(settings)

        if settings.is_turso_enabled:
            from libsql_client import create_client
            from src.scrum.infrastructure.outbox_turso import TursoOutboxClient
            url = settings.turso_url.replace("libsql://", "https://", 1)
            client = create_client(url=url, auth_token=settings.turso_token)
            outbox_client = TursoOutboxClient(client)
        else:
            from src.scrum.infrastructure.outbox_sqlite import SqliteOutboxClient
            conn = await pool.acquire()
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
        if not settings.is_turso_enabled and conn is not None:
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
                await pool.release(conn)
                from src.db.pool import close_pool
                await close_pool()

    return lifespan


def _on_app_init(app_config: AppConfig) -> AppConfig:
    env_file = str(Path(__file__).parents[3] / ".env")
    settings = Settings.from_env(env_file)

    app_config.dependencies["settings"] = Provide(lambda: settings, use_cache=True, sync_to_thread=False)
    app_config.dependencies["pool"] = Provide(get_pool_dependency, use_cache=True)
    app_config.dependencies["proyecto_repo"] = Provide(get_proyecto_repository, use_cache=True)
    app_config.dependencies["usuario_repo"] = Provide(get_usuario_repo, use_cache=True)
    app_config.lifespan.append(_build_lifespan(settings))
    return app_config


def create_app() -> Litestar:
    cors_config = CORSConfig(allow_origins=["*"], allow_credentials=True, max_age=3600)
    return Litestar(
        cors_config=cors_config,
        route_handlers=[
            health,
            profile,
            login,
            register,
            ProyectoController,
        ],
        on_app_init=[_on_app_init, jwt_auth.on_app_init],
        middleware=[RequestLoggingMiddleware, SecurityHeadersMiddleware],
    )
