from __future__ import annotations

from src.shared_kernel.domain.base_exceptions import BusinessRuleError
from src.shared_kernel.domain.base_value_objects import Email, NotEmptyString
from src.idp.domain.value_objects import UserId, UserRole


class Usuario:
    _id: UserId
    _email: Email
    _name: NotEmptyString
    _role: UserRole
    _is_active: bool

    def __init__(
        self,
        email: Email,
        name: NotEmptyString,
        role: UserRole = UserRole.DEVELOPER,
        id: UserId | None = None,
        is_active: bool = True,
    ) -> None:
        self._id = id if id is not None else UserId()
        self._email = email
        self._name = name
        self._role = role
        self._is_active = is_active

    @property
    def id(self) -> UserId:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def name(self) -> NotEmptyString:
        return self._name

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active

    def activate(self) -> None:
        if self._is_active:
            raise BusinessRuleError("User is already active")
        self._is_active = True

    def deactivate(self) -> None:
        if not self._is_active:
            raise BusinessRuleError("User is already inactive")
        self._is_active = False

    def change_role(self, new_role: UserRole) -> None:
        if new_role == self._role:
            raise BusinessRuleError(
                f"User already has role '{new_role.value}'"
            )
        self._role = new_role

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Usuario):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __str__(self) -> str:
        return f"Usuario({self._id}, {self._email})"

    def __repr__(self) -> str:
        return (
            f"Usuario("
            f"id={self._id!r}, "
            f"email={self._email!r}, "
            f"role={self._role!r})"
        )
