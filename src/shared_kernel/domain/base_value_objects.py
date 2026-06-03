from __future__ import annotations

from uuid import UUID, uuid4


class EntityId:
    _value: UUID

    def __init__(self, value: UUID | None = None) -> None:
        self._value = value if value is not None else uuid4()

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityId):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self._value)})"
