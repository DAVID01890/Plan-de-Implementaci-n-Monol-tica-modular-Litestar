from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from libsql_client import create_client

from src.entrypoint.config import Settings
from src.scrum.domain.entities import (
    HistoriaDeUsuario,
    HistoriaId,
    HistoriaStatus,
    Proyecto,
    ProyectoId,
    Sprint,
    SprintId,
    SprintStatus,
)
from src.scrum.domain.value_objects import StoryPoint
from src.scrum.infrastructure.outbox import serialize_event
from src.scrum.ports.proyecto_repository import ProyectoRepository
from src.shared_kernel.domain.base_value_objects import NotEmptyString


def _normalize_url(url: str) -> str:
    return url.replace("libsql://", "https://", 1)


def _row_to_proyecto(id_str: str, nombre: str) -> Proyecto:
    return Proyecto(
        id=ProyectoId(UUID(id_str)),
        nombre=NotEmptyString(nombre),
    )


def _row_to_sprint(
    id_str: str,
    nombre: str,
    fecha_inicio: str | None,
    fecha_fin: str | None,
    status: str,
) -> Sprint:
    return Sprint(
        id=SprintId(UUID(id_str)),
        nombre=NotEmptyString(nombre),
        status=SprintStatus(status),
        fecha_inicio=(
            datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
        ),
        fecha_fin=(
            datetime.fromisoformat(fecha_fin) if fecha_fin else None
        ),
    )


def _row_to_historia(
    id_str: str,
    titulo: str,
    descripcion: str | None,
    story_points: int,
    status: str,
) -> HistoriaDeUsuario:
    return HistoriaDeUsuario(
        id=HistoriaId(UUID(id_str)),
        title=NotEmptyString(titulo),
        story_points=StoryPoint(story_points),
        description=descripcion,
        status=HistoriaStatus(status),
    )


class ProyectoRepositorioTurso(ProyectoRepository):
    def __init__(self, settings: Settings | None = None) -> None:
        s = settings if settings is not None else Settings.from_env()
        if not s.is_turso_enabled:
            raise RuntimeError(
                "Turso is not configured. Set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN."
            )
        self._url = _normalize_url(s.turso_url)
        self._token = s.turso_token

    async def save(self, proyecto: Proyecto) -> None:
        stmts: list[tuple[str, tuple]] = [
            (
                "INSERT OR REPLACE INTO proyectos (id, nombre) VALUES (?, ?)",
                (str(proyecto.id), str(proyecto.nombre)),
            )
        ]
        for sprint in proyecto.sprints:
            fecha_inicio = (
                sprint.fecha_inicio.isoformat()
                if sprint.fecha_inicio
                else None
            )
            fecha_fin = (
                sprint.fecha_fin.isoformat()
                if sprint.fecha_fin
                else None
            )
            stmts.append(
                (
                    "INSERT OR REPLACE INTO sprints "
                    "(id, proyecto_id, nombre, fecha_inicio, fecha_fin, status) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        str(sprint.id),
                        str(proyecto.id),
                        str(sprint.nombre),
                        fecha_inicio,
                        fecha_fin,
                        sprint.status.value,
                    ),
                )
            )
        for historia in proyecto.historias:
            stmts.append(
                (
                    "INSERT OR REPLACE INTO historias "
                    "(id, proyecto_id, titulo, descripcion, story_points, status) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        str(historia.id),
                        str(proyecto.id),
                        str(historia.title),
                        historia.description,
                        historia.story_points.value,
                        historia.status.value,
                    ),
                )
            )
        for sprint in proyecto.sprints:
            for historia_id in sprint.backlog:
                stmts.append(
                    (
                        "UPDATE historias SET sprint_id = ? WHERE id = ?",
                        (str(sprint.id), str(historia_id)),
                    )
                )

        events = proyecto.pull_domain_events()
        for event in events:
            event_id, event_type, payload, occurred_at, created_at = serialize_event(event)
            stmts.append(
                (
                    "INSERT INTO outbox_events "
                    "(id, aggregate_id, event_type, payload, occurred_at, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        event_id,
                        str(proyecto.id),
                        event_type,
                        payload,
                        occurred_at,
                        created_at,
                    ),
                )
            )

        client = create_client(url=self._url, auth_token=self._token)
        try:
            await client.batch(stmts)
        finally:
            await client.close()

    async def find_by_id(self, proyecto_id: ProyectoId) -> Proyecto | None:
        client = create_client(url=self._url, auth_token=self._token)
        try:
            result = await client.execute(
                "SELECT id, nombre FROM proyectos WHERE id = ?",
                (str(proyecto_id),),
            )
            if not result.rows:
                return None

            row = result.rows[0]
            proyecto = _row_to_proyecto(row["id"], row["nombre"])

            result = await client.execute(
                "SELECT id, nombre, fecha_inicio, fecha_fin, status "
                "FROM sprints WHERE proyecto_id = ?",
                (str(proyecto_id),),
            )
            sprint_map: dict[str, Sprint] = {}
            for row in result.rows:
                sprint = _row_to_sprint(
                    row["id"],
                    row["nombre"],
                    row["fecha_inicio"],
                    row["fecha_fin"],
                    row["status"],
                )
                sprint_map[row["id"]] = sprint
                proyecto._sprints[sprint.id] = sprint

            result = await client.execute(
                "SELECT id, titulo, descripcion, story_points, status, sprint_id "
                "FROM historias WHERE proyecto_id = ?",
                (str(proyecto_id),),
            )
            for row in result.rows:
                historia = _row_to_historia(
                    row["id"],
                    row["titulo"],
                    row["descripcion"],
                    row["story_points"],
                    row["status"],
                )
                proyecto._historias[historia.id] = historia
                sprint_id_str = None
                try:
                    sprint_id_str = row["sprint_id"]
                except KeyError:
                    pass
                if sprint_id_str and sprint_id_str in sprint_map:
                    sprint_map[sprint_id_str]._backlog.append(historia.id)

            return proyecto
        finally:
            await client.close()

    async def list(self) -> list[Proyecto]:
        client = create_client(url=self._url, auth_token=self._token)
        try:
            result = await client.execute(
                "SELECT id, nombre FROM proyectos ORDER BY nombre"
            )
            return [_row_to_proyecto(row["id"], row["nombre"]) for row in result.rows]
        finally:
            await client.close()

    async def delete(self, proyecto_id: ProyectoId) -> None:
        stmts: list[tuple[str, tuple]] = [
            (
                "DELETE FROM tareas_tecnicas "
                "WHERE historia_id IN (SELECT id FROM historias WHERE proyecto_id = ?)",
                (str(proyecto_id),),
            ),
            (
                "DELETE FROM historias WHERE proyecto_id = ?",
                (str(proyecto_id),),
            ),
            (
                "DELETE FROM sprints WHERE proyecto_id = ?",
                (str(proyecto_id),),
            ),
            (
                "DELETE FROM proyectos WHERE id = ?",
                (str(proyecto_id),),
            ),
        ]
        client = create_client(url=self._url, auth_token=self._token)
        try:
            await client.batch(stmts)
        finally:
            await client.close()
