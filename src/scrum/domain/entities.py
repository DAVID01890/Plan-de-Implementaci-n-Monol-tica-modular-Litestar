from __future__ import annotations

from enum import Enum

from src.scrum.domain.value_objects import StoryPoint
from src.shared_kernel.domain.base_exceptions import BusinessRuleError
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
