from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException
from litestar.handlers.base import BaseRouteHandler
from litestar.security.jwt import JWTAuth
from litestar.security.jwt.token import Token

from src.entrypoint.auth.config import AuthSettings
from src.idp.domain.entities import Usuario
from src.idp.domain.value_objects import UserId
from src.shared_kernel.infrastructure.cache import TTLCache

logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parents[3] / ".env")
settings = AuthSettings.from_env()

_user_cache: TTLCache[Usuario] = TTLCache[Usuario](ttl_seconds=30.0, maxsize=256)


async def retrieve_user_handler(token: Token, connection: ASGIConnection) -> Usuario | None:
    from src.entrypoint.config import Settings as AppSettings

    app_settings = AppSettings.from_env()
    user_id = str(token.sub)
    cached = await _user_cache.get(user_id)
    if cached is not None:
        logger.debug("Cache hit for user %s", user_id)
        return cached

    if app_settings.is_turso_enabled:
        from src.idp.adapters.usuario_repo_turso import (
            UsuarioRepositorioTurso,
        )
        repo = UsuarioRepositorioTurso(app_settings)
    else:
        from src.idp.adapters.usuario_repo_sqlite import (
            UsuarioRepositorySQLite,
        )
        repo = UsuarioRepositorySQLite()

    user = await repo.find_by_id(UserId(UUID(user_id)))
    if user is not None:
        await _user_cache.set(user_id, user)
    return user


jwt_auth = JWTAuth(
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.secret,
    exclude=["/health", "/debug/profile", "/auth/login", "/auth/register", "/schema"],
)


async def require_active_user(
    connection: ASGIConnection,
    handler: BaseRouteHandler,
) -> None:
    user: Usuario | None = connection.user
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
