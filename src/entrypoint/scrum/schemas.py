from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class CreateProyectoRequest:
    nombre: str


@dataclass
class CreateHistoriaRequest:
    titulo: str
    story_points: int
    descripcion: str | None = None


@dataclass
class CreateSprintRequest:
    nombre: str


@dataclass
class AddHistoriaToSprintRequest:
    historia_id: str
    sprint_id: str


@dataclass
class HistoriaResponse:
    id: str
    titulo: str
    descripcion: str | None
    story_points: int
    status: str


@dataclass
class SprintResponse:
    id: str
    nombre: str
    status: str
    fecha_inicio: str | None
    fecha_fin: str | None
    backlog: list[str]


@dataclass
class ProyectoResponse:
    id: str
    nombre: str
    sprints: list[SprintResponse] = field(default_factory=list)
    historias: list[HistoriaResponse] = field(default_factory=list)
