"""MCP server for PoC Planner — expone las herramientas del dominio directamente."""
from __future__ import annotations

import sys
from uuid import UUID

from mcp.server.fastmcp import FastMCP

from src.entrypoint.config import Settings
from src.idp.domain.entities import Usuario
from src.idp.domain.value_objects import UserId, UserRole
from src.scrum.domain.entities import (
    HistoriaDeUsuario,
    HistoriaId,
    Proyecto,
    ProyectoId,
    Sprint,
    SprintId,
)
from src.scrum.domain.value_objects import StoryPoint
from src.shared_kernel.domain.base_exceptions import ValidationError
from src.shared_kernel.domain.base_value_objects import Email, NotEmptyString

mcp = FastMCP("PoC Planner", host="0.0.0.0", port=8100)
settings = Settings.from_env()
_pool = None
_db_initialized = False


async def _get_pool():
    global _pool
    if _pool is None:
        from src.db.pool import get_pool
        _pool = await get_pool(settings)
    return _pool


async def _ensure_pool():
    if not settings.is_turso_enabled and _pool is None:
        await _get_pool()


async def _init():
    global _db_initialized
    if _db_initialized:
        return
    await _ensure_pool()
    from src.db.connection import init_db
    await init_db(settings)
    _db_initialized = True


def _get_proyecto_repo():
    if settings.is_turso_enabled:
        from src.scrum.adapters.proyecto_repo_turso import (
            ProyectoRepositorioTurso,
        )
        return ProyectoRepositorioTurso(settings)
    from src.scrum.adapters.proyecto_repo_sqlite import (
        ProyectoRepositorySQLite,
    )
    return ProyectoRepositorySQLite(pool=_pool)


def _get_usuario_repo():
    if settings.is_turso_enabled:
        from src.idp.adapters.usuario_repo_turso import (
            UsuarioRepositorioTurso,
        )
        return UsuarioRepositorioTurso(settings)
    from src.idp.adapters.usuario_repo_sqlite import (
        UsuarioRepositorySQLite,
    )
    return UsuarioRepositorySQLite()


@mcp.tool()
async def health() -> dict:
    """Verifica que la base de datos responde."""
    try:
        await _init()
        if settings.is_turso_enabled:
            from libsql_client import create_client
            url = settings.turso_url.replace("libsql://", "https://", 1)
            client = create_client(url=url, auth_token=settings.turso_token)
            await client.execute("SELECT 1")
            await client.close()
        else:
            async with _pool.connection() as conn:
                await conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": str(e)}


@mcp.tool()
async def register_user(email: str, password: str) -> dict:
    """Registra un nuevo usuario en el sistema."""
    try:
        email_vo = Email(email)
    except Exception as e:
        return {"error": f"Email invalido: {e}"}

    await _init()
    repo = _get_usuario_repo()
    existing = await repo.find_by_email(email_vo)
    if existing is not None:
        return {"error": "Email ya registrado"}

    user = Usuario(
        id=UserId(),
        email=email_vo,
        name=NotEmptyString(email.split("@")[0]),
        role=UserRole.DEVELOPER,
        is_active=True,
    )
    user.set_password(password)
    await repo.save(user)
    return {"id": str(user.id), "email": str(user.email)}


@mcp.tool()
async def login_user(email: str, password: str) -> dict:
    """Autentica un usuario y devuelve un token JWT."""
    try:
        email_vo = Email(email)
    except Exception as e:
        return {"error": f"Email invalido: {e}"}

    await _init()
    repo = _get_usuario_repo()
    user = await repo.find_by_email(email_vo)
    if user is None or not user.verify_password(password):
        return {"error": "Credenciales invalidas"}
    if not user.is_active:
        return {"error": "Cuenta inactiva"}

    from litestar.security.jwt import JWTAuth
    token = JWTAuth(
        retrieve_user_handler=lambda t, c: None,
        token_secret=settings.jwt_secret,
    ).create_token(identifier=str(user.id))
    return {"access_token": token, "token_type": "Bearer"}


@mcp.tool()
async def create_proyecto(nombre: str) -> dict:
    """Crea un nuevo proyecto."""
    try:
        nombre_vo = NotEmptyString(nombre)
    except ValidationError as e:
        return {"error": str(e)}

    await _init()
    proyecto = Proyecto.create(nombre=nombre_vo)
    repo = _get_proyecto_repo()
    await repo.save(proyecto)
    return {"id": str(proyecto.id), "nombre": str(proyecto.nombre)}


@mcp.tool()
async def list_proyectos() -> dict:
    """Lista todos los proyectos."""
    await _ensure_pool()
    repo = _get_proyecto_repo()
    proyectos = await repo.list()
    return {"proyectos": [{"id": str(p.id), "nombre": str(p.nombre)} for p in proyectos]}


@mcp.tool()
async def get_proyecto(proyecto_id: str) -> dict:
    """Obtiene un proyecto con sus sprints e historias."""
    try:
        pid = ProyectoId(UUID(proyecto_id))
    except (ValueError, TypeError):
        return {"error": "ID de proyecto invalido"}

    await _ensure_pool()
    repo = _get_proyecto_repo()
    proyecto = await repo.find_by_id(pid)
    if proyecto is None:
        return {"error": "Proyecto no encontrado"}

    return {
        "id": str(proyecto.id),
        "nombre": str(proyecto.nombre),
        "sprints": [
            {
                "id": str(s.id),
                "nombre": str(s.nombre),
                "status": s.status.value,
            }
            for s in proyecto.sprints
        ],
        "historias": [
            {
                "id": str(h.id),
                "titulo": str(h.title),
                "story_points": h.story_points.value,
                "status": h.status.value,
            }
            for h in proyecto.historias
        ],
    }


@mcp.tool()
async def add_historia(proyecto_id: str, titulo: str, story_points: int) -> dict:
    """Agrega una historia de usuario a un proyecto."""
    try:
        pid = ProyectoId(UUID(proyecto_id))
    except (ValueError, TypeError):
        return {"error": "ID de proyecto invalido"}
    try:
        historia = HistoriaDeUsuario(
            title=NotEmptyString(titulo),
            story_points=StoryPoint(story_points),
        )
    except ValidationError as e:
        return {"error": str(e)}

    await _init()
    repo = _get_proyecto_repo()
    proyecto = await repo.find_by_id(pid)
    if proyecto is None:
        return {"error": "Proyecto no encontrado"}
    proyecto.add_historia(historia)
    await repo.save(proyecto)
    return {"id": str(historia.id), "titulo": titulo, "story_points": story_points}


@mcp.tool()
async def create_sprint(proyecto_id: str, nombre: str) -> dict:
    """Crea un sprint en un proyecto."""
    try:
        pid = ProyectoId(UUID(proyecto_id))
    except (ValueError, TypeError):
        return {"error": "ID de proyecto invalido"}

    await _init()
    repo = _get_proyecto_repo()
    proyecto = await repo.find_by_id(pid)
    if proyecto is None:
        return {"error": "Proyecto no encontrado"}
    try:
        sprint = proyecto.create_sprint(nombre=NotEmptyString(nombre))
    except (ValidationError, Exception) as e:
        return {"error": str(e)}
    await repo.save(proyecto)
    return {"id": str(sprint.id), "nombre": nombre, "status": sprint.status.value}


@mcp.tool()
async def assign_historia_to_sprint(
    proyecto_id: str, historia_id: str, sprint_id: str
) -> dict:
    """Asigna una historia de usuario a un sprint."""
    try:
        pid = ProyectoId(UUID(proyecto_id))
        hid = HistoriaId(UUID(historia_id))
        sid = SprintId(UUID(sprint_id))
    except (ValueError, TypeError):
        return {"error": "ID invalido"}

    await _init()
    repo = _get_proyecto_repo()
    proyecto = await repo.find_by_id(pid)
    if proyecto is None:
        return {"error": "Proyecto no encontrado"}
    try:
        proyecto.add_historia_to_sprint(hid, sid)
    except Exception as e:
        return {"error": str(e)}
    await repo.save(proyecto)
    return {"status": "ok", "historia": historia_id, "sprint": sprint_id}


@mcp.tool()
async def start_sprint(proyecto_id: str, sprint_id: str) -> dict:
    """Inicia un sprint (lo pasa de planned a active)."""
    try:
        pid = ProyectoId(UUID(proyecto_id))
        sid = SprintId(UUID(sprint_id))
    except (ValueError, TypeError):
        return {"error": "ID invalido"}

    await _init()
    repo = _get_proyecto_repo()
    proyecto = await repo.find_by_id(pid)
    if proyecto is None:
        return {"error": "Proyecto no encontrado"}
    try:
        proyecto.start_sprint(sid)
    except Exception as e:
        return {"error": str(e)}
    await repo.save(proyecto)
    sprint = proyecto.get_sprint(sid)
    return {
        "status": "ok",
        "sprint_status": sprint.status.value,
        "fecha_inicio": (
            sprint.fecha_inicio.isoformat() if sprint.fecha_inicio else None
        ),
    }


if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)
