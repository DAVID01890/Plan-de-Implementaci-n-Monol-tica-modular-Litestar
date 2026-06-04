from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from src.scrum.domain.value_objects import HorasEstimadas, StoryPoint
from src.shared_kernel.domain.base_exceptions import BusinessRuleError, NotFoundError
from src.scrum.domain.events import (
    HistoriaAgregada,
    HistoriaAsignadaASprint,
    ProyectoCreado,
    SprintCreado,
    SprintIniciado,
)
from src.shared_kernel.domain.base_events import DomainEvent
from src.shared_kernel.domain.base_value_objects import EntityId, NotEmptyString


class HistoriaId(EntityId):
    pass


class HistoriaStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class HistoriaDeUsuario:
    _id: HistoriaId
    _title: NotEmptyString
    _description: str | None
    _story_points: StoryPoint
    _status: HistoriaStatus

    def __init__(
        self,
        title: NotEmptyString,
        story_points: StoryPoint,
        description: str | None = None,
        status: HistoriaStatus = HistoriaStatus.PENDING,
        id: HistoriaId | None = None,
    ) -> None:
        self._id = id if id is not None else HistoriaId()
        self._title = title
        self._description = description
        self._story_points = story_points
        self._status = status

    @property
    def id(self) -> HistoriaId:
        return self._id

    @property
    def title(self) -> NotEmptyString:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def story_points(self) -> StoryPoint:
        return self._story_points

    @property
    def status(self) -> HistoriaStatus:
        return self._status

    def start_work(self) -> None:
        if self._status != HistoriaStatus.PENDING:
            raise BusinessRuleError(
                f"Cannot start work on a {self._status.value} historia"
            )
        self._status = HistoriaStatus.IN_PROGRESS

    def complete(self) -> None:
        if self._status != HistoriaStatus.IN_PROGRESS:
            raise BusinessRuleError(
                f"Cannot complete a {self._status.value} historia"
            )
        self._status = HistoriaStatus.DONE

    def reopen(self) -> None:
        if self._status != HistoriaStatus.DONE:
            raise BusinessRuleError(
                f"Cannot reopen a {self._status.value} historia"
            )
        self._status = HistoriaStatus.PENDING

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HistoriaDeUsuario):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __str__(self) -> str:
        return f"HistoriaDeUsuario({self._id}, {self._title})"

    def __repr__(self) -> str:
        return (
            f"HistoriaDeUsuario("
            f"id={self._id!r}, "
            f"title={self._title!r}, "
            f"points={self._story_points!r})"
        )


class TareaTecnicaId(EntityId):
    pass


class TareaTecnicaStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TareaTecnica:
    _id: TareaTecnicaId
    _historia_id: HistoriaId
    _title: NotEmptyString
    _description: str | None
    _estimated_hours: HorasEstimadas
    _status: TareaTecnicaStatus

    def __init__(
        self,
        historia_id: HistoriaId,
        title: NotEmptyString,
        estimated_hours: HorasEstimadas,
        description: str | None = None,
        status: TareaTecnicaStatus = TareaTecnicaStatus.PENDING,
        id: TareaTecnicaId | None = None,
    ) -> None:
        self._id = id if id is not None else TareaTecnicaId()
        self._historia_id = historia_id
        self._title = title
        self._description = description
        self._estimated_hours = estimated_hours
        self._status = status

    @property
    def id(self) -> TareaTecnicaId:
        return self._id

    @property
    def historia_id(self) -> HistoriaId:
        return self._historia_id

    @property
    def title(self) -> NotEmptyString:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def estimated_hours(self) -> HorasEstimadas:
        return self._estimated_hours

    @property
    def status(self) -> TareaTecnicaStatus:
        return self._status

    def start_work(self) -> None:
        if self._status != TareaTecnicaStatus.PENDING:
            raise BusinessRuleError(
                f"Cannot start work on a {self._status.value} tarea"
            )
        self._status = TareaTecnicaStatus.IN_PROGRESS

    def complete(self) -> None:
        if self._status != TareaTecnicaStatus.IN_PROGRESS:
            raise BusinessRuleError(
                f"Cannot complete a {self._status.value} tarea"
            )
        self._status = TareaTecnicaStatus.DONE

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TareaTecnica):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __str__(self) -> str:
        return f"TareaTecnica({self._id}, {self._title})"

    def __repr__(self) -> str:
        return (
            f"TareaTecnica("
            f"id={self._id!r}, "
            f"historia_id={self._historia_id!r}, "
            f"title={self._title!r})"
        )


class SprintId(EntityId):
    pass


class SprintStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    CLOSED = "closed"


class Sprint:
    _id: SprintId
    _nombre: NotEmptyString
    _fecha_inicio: datetime | None
    _fecha_fin: datetime | None
    _status: SprintStatus
    _backlog: list[HistoriaId]

    def __init__(
        self,
        nombre: NotEmptyString,
        status: SprintStatus = SprintStatus.PLANNED,
        fecha_inicio: datetime | None = None,
        fecha_fin: datetime | None = None,
        id: SprintId | None = None,
    ) -> None:
        self._id = id if id is not None else SprintId()
        self._nombre = nombre
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin
        self._status = status
        self._backlog = []

    @property
    def id(self) -> SprintId:
        return self._id

    @property
    def nombre(self) -> NotEmptyString:
        return self._nombre

    @property
    def fecha_inicio(self) -> datetime | None:
        return self._fecha_inicio

    @property
    def fecha_fin(self) -> datetime | None:
        return self._fecha_fin

    @property
    def status(self) -> SprintStatus:
        return self._status

    @property
    def backlog(self) -> list[HistoriaId]:
        return list(self._backlog)

    def start(self, fecha_inicio: datetime | None = None) -> None:
        if self._status is not SprintStatus.PLANNED:
            raise BusinessRuleError(
                f"Cannot start a {self._status.value} sprint"
            )
        self._status = SprintStatus.ACTIVE
        self._fecha_inicio = (
            fecha_inicio if fecha_inicio is not None else datetime.now(timezone.utc)
        )

    def close(self, fecha_fin: datetime | None = None) -> None:
        if self._status is not SprintStatus.ACTIVE:
            raise BusinessRuleError(
                f"Cannot close a {self._status.value} sprint"
            )
        self._status = SprintStatus.CLOSED
        self._fecha_fin = (
            fecha_fin if fecha_fin is not None else datetime.now(timezone.utc)
        )

    def add_historia(self, historia_id: HistoriaId) -> None:
        if self._status is SprintStatus.CLOSED:
            raise BusinessRuleError(
                f"Cannot add historias to a {self._status.value} sprint"
            )
        if historia_id in self._backlog:
            raise BusinessRuleError(
                f"Historia '{historia_id}' is already in sprint '{self._id}'"
            )
        self._backlog.append(historia_id)

    def remove_historia(self, historia_id: HistoriaId) -> None:
        if self._status is SprintStatus.CLOSED:
            raise BusinessRuleError(
                f"Cannot remove historias from a {self._status.value} sprint"
            )
        if historia_id not in self._backlog:
            raise NotFoundError("HistoriaDeUsuario", str(historia_id))
        self._backlog = [h for h in self._backlog if h != historia_id]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sprint):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __str__(self) -> str:
        return f"Sprint({self._id}, {self._nombre})"

    def __repr__(self) -> str:
        return (
            f"Sprint("
            f"id={self._id!r}, "
            f"nombre={self._nombre!r}, "
            f"status={self._status!r})"
        )


class ProyectoId(EntityId):
    pass


class Proyecto:
    _id: ProyectoId
    _nombre: NotEmptyString
    _sprints: dict[SprintId, Sprint]
    _historias: dict[HistoriaId, HistoriaDeUsuario]
    _domain_events: list[DomainEvent]

    def __init__(
        self,
        nombre: NotEmptyString,
        id: ProyectoId | None = None,
    ) -> None:
        self._id = id if id is not None else ProyectoId()
        self._nombre = nombre
        self._sprints = {}
        self._historias = {}
        self._domain_events = []

    @classmethod
    def create(cls, nombre: NotEmptyString) -> Proyecto:
        proyecto = cls(nombre=nombre)
        proyecto._register_event(
            ProyectoCreado(
                proyecto_id=str(proyecto.id),
                nombre=str(nombre),
            )
        )
        return proyecto

    def _register_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    @property
    def id(self) -> ProyectoId:
        return self._id

    @property
    def nombre(self) -> NotEmptyString:
        return self._nombre

    @property
    def sprints(self) -> list[Sprint]:
        return list(self._sprints.values())

    @property
    def historias(self) -> list[HistoriaDeUsuario]:
        return list(self._historias.values())

    def add_historia(self, historia: HistoriaDeUsuario) -> None:
        if historia.id in self._historias:
            raise BusinessRuleError(
                f"Historia '{historia.id}' already exists in proyecto '{self._id}'"
            )
        self._historias[historia.id] = historia
        self._register_event(
            HistoriaAgregada(
                proyecto_id=str(self._id),
                historia_id=str(historia.id),
                titulo=str(historia.title),
                story_points=historia.story_points.value,
            )
        )

    def create_sprint(self, nombre: NotEmptyString) -> Sprint:
        sprint = Sprint(nombre=nombre)
        self._sprints[sprint.id] = sprint
        self._register_event(
            SprintCreado(
                proyecto_id=str(self._id),
                sprint_id=str(sprint.id),
                nombre=str(nombre),
            )
        )
        return sprint

    def add_historia_to_sprint(
        self, historia_id: HistoriaId, sprint_id: SprintId
    ) -> None:
        if historia_id not in self._historias:
            raise NotFoundError("HistoriaDeUsuario", str(historia_id))
        if sprint_id not in self._sprints:
            raise NotFoundError("Sprint", str(sprint_id))

        sprint = self._sprints[sprint_id]

        if sprint.status is SprintStatus.ACTIVE:
            for existing_sprint in self._sprints.values():
                if existing_sprint.id == sprint_id:
                    continue
                if (
                    existing_sprint.status is SprintStatus.ACTIVE
                    and historia_id in existing_sprint.backlog
                ):
                    raise BusinessRuleError(
                        f"Historia '{historia_id}' is already in active sprint "
                        f"'{existing_sprint.id}'"
                    )

        sprint.add_historia(historia_id)
        self._register_event(
            HistoriaAsignadaASprint(
                proyecto_id=str(self._id),
                sprint_id=str(sprint_id),
                historia_id=str(historia_id),
            )
        )

    def start_sprint(
        self, sprint_id: SprintId, fecha_inicio: datetime | None = None
    ) -> None:
        sprint = self.get_sprint(sprint_id)
        sprint.start(fecha_inicio)
        self._register_event(
            SprintIniciado(
                proyecto_id=str(self._id),
                sprint_id=str(sprint.id),
                fecha_inicio=str(sprint.fecha_inicio),
            )
        )

    def get_sprint(self, sprint_id: SprintId) -> Sprint:
        if sprint_id not in self._sprints:
            raise NotFoundError("Sprint", str(sprint_id))
        return self._sprints[sprint_id]

    def get_historia(self, historia_id: HistoriaId) -> HistoriaDeUsuario:
        if historia_id not in self._historias:
            raise NotFoundError("HistoriaDeUsuario", str(historia_id))
        return self._historias[historia_id]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Proyecto):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __str__(self) -> str:
        return f"Proyecto({self._id}, {self._nombre})"

    def __repr__(self) -> str:
        return (
            f"Proyecto("
            f"id={self._id!r}, "
            f"nombre={self._nombre!r})"
        )
