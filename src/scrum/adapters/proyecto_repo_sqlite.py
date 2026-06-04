from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import aiosqlite

from src.db.connection import get_sqlite_connection
from src.scrum.infrastructure.outbox import serialize_event
from src.scrum.domain.entities import (
    HistoriaDeUsuario,
    HistoriaId,
    HistoriaStatus,
    Proyecto,
    ProyectoId,
    Sprint,
    SprintId,
    SprintStatus,
    TareaTecnica,
    TareaTecnicaId,
    TareaTecnicaStatus,
)
from src.scrum.domain.value_objects import HorasEstimadas, StoryPoint
from src.scrum.ports.proyecto_repository import ProyectoRepository
from src.shared_kernel.domain.base_value_objects import NotEmptyString


def _row_to_proyecto(row: aiosqlite.Row) -> Proyecto:
    return Proyecto(
        id=ProyectoId(UUID(row["id"])),
        nombre=NotEmptyString(row["nombre"]),
    )


def _row_to_sprint(row: aiosqlite.Row) -> Sprint:
    fecha_inicio = (
        datetime.fromisoformat(row["fecha_inicio"])
        if row["fecha_inicio"]
        else None
    )
    fecha_fin = (
        datetime.fromisoformat(row["fecha_fin"]) if row["fecha_fin"] else None
    )
    return Sprint(
        id=SprintId(UUID(row["id"])),
        nombre=NotEmptyString(row["nombre"]),
        status=SprintStatus(row["status"]),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def _row_to_historia(row: aiosqlite.Row) -> HistoriaDeUsuario:
    return HistoriaDeUsuario(
        id=HistoriaId(UUID(row["id"])),
        title=NotEmptyString(row["titulo"]),
        story_points=StoryPoint(row["story_points"]),
        description=row["descripcion"],
        status=HistoriaStatus(row["status"]),
    )


class ProyectoRepositorySQLite(ProyectoRepository):
    async def save(self, proyecto: Proyecto) -> None:
        async with get_sqlite_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO proyectos (id, nombre) VALUES (?, ?)",
                (str(proyecto.id), str(proyecto.nombre)),
            )
            for sprint in proyecto.sprints:
                fecha_inicio = (
                    sprint.fecha_inicio.isoformat()
                    if sprint.fecha_inicio
                    else None
                )
                fecha_fin = (
                    sprint.fecha_fin.isoformat() if sprint.fecha_fin else None
                )
                await conn.execute(
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
            for historia in proyecto.historias:
                await conn.execute(
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
            for sprint in proyecto.sprints:
                for historia_id in sprint.backlog:
                    await conn.execute(
                        "UPDATE historias SET sprint_id = ? WHERE id = ?",
                        (str(sprint.id), str(historia_id)),
                    )
            events = proyecto.pull_domain_events()
            for event in events:
                event_id, event_type, payload, occurred_at, created_at = serialize_event(event)
                await conn.execute(
                    "INSERT INTO outbox_events "
                    "(id, aggregate_id, event_type, payload, occurred_at, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (event_id, str(proyecto.id), event_type, payload, occurred_at, created_at),
                )
            await conn.commit()

    async def find_by_id(self, proyecto_id: ProyectoId) -> Proyecto | None:
        async with get_sqlite_connection() as conn:
            cursor = await conn.execute(
                "SELECT id, nombre FROM proyectos WHERE id = ?",
                (str(proyecto_id),),
            )
            row = await cursor.fetchone()
            if row is None:
                return None

            proyecto = _row_to_proyecto(row)

            cursor = await conn.execute(
                "SELECT id, nombre, fecha_inicio, fecha_fin, status "
                "FROM sprints WHERE proyecto_id = ?",
                (str(proyecto_id),),
            )
            sprint_rows = await cursor.fetchall()
            sprint_map: dict[str, Sprint] = {}
            for srow in sprint_rows:
                sprint = _row_to_sprint(srow)
                sprint_map[str(sprint.id)] = sprint
                proyecto._sprints[sprint.id] = sprint

            cursor = await conn.execute(
                "SELECT id, titulo, descripcion, story_points, status, sprint_id "
                "FROM historias WHERE proyecto_id = ?",
                (str(proyecto_id),),
            )
            historia_rows = await cursor.fetchall()
            for hrow in historia_rows:
                historia = _row_to_historia(hrow)
                proyecto._historias[historia.id] = historia
                sprint_id_str = hrow["sprint_id"]
                if sprint_id_str and sprint_id_str in sprint_map:
                    sprint_map[sprint_id_str]._backlog.append(historia.id)

            return proyecto

    async def list(self) -> list[Proyecto]:
        async with get_sqlite_connection() as conn:
            cursor = await conn.execute(
                "SELECT id, nombre FROM proyectos ORDER BY nombre"
            )
            rows = await cursor.fetchall()
        return [_row_to_proyecto(row) for row in rows]

    async def delete(self, proyecto_id: ProyectoId) -> None:
        async with get_sqlite_connection() as conn:
            await conn.execute(
                "DELETE FROM tareas_tecnicas "
                "WHERE historia_id IN (SELECT id FROM historias WHERE proyecto_id = ?)",
                (str(proyecto_id),),
            )
            await conn.execute(
                "DELETE FROM historias WHERE proyecto_id = ?",
                (str(proyecto_id),),
            )
            await conn.execute(
                "DELETE FROM sprints WHERE proyecto_id = ?",
                (str(proyecto_id),),
            )
            await conn.execute(
                "DELETE FROM proyectos WHERE id = ?",
                (str(proyecto_id),),
            )
            await conn.commit()
