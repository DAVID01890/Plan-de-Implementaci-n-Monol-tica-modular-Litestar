from __future__ import annotations

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

load_dotenv(Path(__file__).parents[3] / ".env")
settings = AuthSettings.from_env()


async def retrieve_user_handler(token: Token, connection: ASGIConnection) -> Usuario | None:
    from src.idp.adapters.usuario_repo_sqlite import (
        UsuarioRepositorySQLite,
    )

    repo = UsuarioRepositorySQLite()
    return await repo.find_by_id(UserId(UUID(token.sub)))


jwt_auth = JWTAuth(
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.secret,
    exclude=["/health", "/auth/login", "/auth/register", "/schema"],
)


async def require_active_user(
    connection: ASGIConnection,
    handler: BaseRouteHandler,
) -> None:
    user: Usuario | None = connection.user
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
