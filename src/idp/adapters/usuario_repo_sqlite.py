from __future__ import annotations

from uuid import UUID

from src.db.connection import get_sqlite_connection
from src.idp.domain.entities import Usuario
from src.idp.domain.value_objects import UserId, UserRole
from src.idp.ports.usuario_repository import UsuarioRepository
from src.shared_kernel.domain.base_value_objects import Email, NotEmptyString


class UsuarioRepositorySQLite(UsuarioRepository):
    async def save(self, usuario: Usuario) -> None:
        async with get_sqlite_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO usuarios (id, email, name, role, is_active) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    str(usuario.id),
                    str(usuario.email),
                    str(usuario.name),
                    usuario.role.value,
                    1 if usuario.is_active else 0,
                ),
            )
            await conn.commit()

    async def find_by_id(self, user_id: UserId) -> Usuario | None:
        async with get_sqlite_connection() as conn:
            cursor = await conn.execute(
                "SELECT id, email, name, role, is_active FROM usuarios WHERE id = ?",
                (str(user_id),),
            )
            row = await cursor.fetchone()
        return self._row_to_usuario(row) if row else None

    async def find_by_email(self, email: Email) -> Usuario | None:
        async with get_sqlite_connection() as conn:
            cursor = await conn.execute(
                "SELECT id, email, name, role, is_active FROM usuarios WHERE email = ?",
                (str(email),),
            )
            row = await cursor.fetchone()
        return self._row_to_usuario(row) if row else None

    async def list(self) -> list[Usuario]:
        async with get_sqlite_connection() as conn:
            cursor = await conn.execute(
                "SELECT id, email, name, role, is_active FROM usuarios ORDER BY email"
            )
            rows = await cursor.fetchall()
        return [self._row_to_usuario(row) for row in rows]

    async def delete(self, user_id: UserId) -> None:
        async with get_sqlite_connection() as conn:
            await conn.execute(
                "DELETE FROM usuarios WHERE id = ?",
                (str(user_id),),
            )
            await conn.commit()

    @staticmethod
    def _row_to_usuario(row) -> Usuario:
        return Usuario(
            id=UserId(UUID(row["id"])),
            email=Email(row["email"]),
            name=NotEmptyString(row["name"]),
            role=UserRole(row["role"]),
            is_active=bool(row["is_active"]),
        )
