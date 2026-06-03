# Sesión 07 — El Puerto IdentityServicePort (Interfaz y Mock)

- **Fecha:** 2026-06-03
- **Fase:** 3 — Proveedor de Identidad (IdP — Dominio y Puerto)
- **Estado:** ✅ Completada

---

## Objetivo

Definir el puerto (interfaz) `IdentityServicePort` y su implementación Mock para el módulo IdP.

**Criterio de éxito:** Tests que verifiquen el contrato del puerto usando el Mock.

---

## Implementación

### `src/idp/ports/identity_service_port.py` — Puerto (interfaz)

```python
class IdentityServicePort(ABC):
    @abstractmethod
    def create_user(self, email: Email, name: NotEmptyString,
                    role: UserRole = UserRole.DEVELOPER) -> Usuario: ...
    @abstractmethod
    def get_by_id(self, user_id: UserId) -> Usuario | None: ...
    @abstractmethod
    def get_by_email(self, email: Email) -> Usuario | None: ...
    @abstractmethod
    def list_users(self) -> list[Usuario]: ...
    @abstractmethod
    def update_role(self, user_id: UserId, new_role: UserRole) -> Usuario: ...
```

**Conceptos clave:**
- **ABC + `@abstractmethod`**: Define el contrato sin implementación. Cualquier adapter debe cumplir con esta firma.
- **Operaciones CRUD**: crear, leer por ID, leer por email, listar, actualizar rol — cubre los casos de uso básicos de IdP

### `src/idp/adapters/mock/identity_service_mock.py` — Mock

```python
class IdentityServiceMock(IdentityServicePort):
    _users: dict[str, Usuario]

    def create_user(self, email, name, role=UserRole.DEVELOPER) -> Usuario:
        # Valida que el email no esté duplicado → BusinessRuleError
        user = Usuario(email=email, name=name, role=role)
        self._users[str(user.id)] = user
        return user

    def update_role(self, user_id, new_role) -> Usuario:
        # Busca por ID → NotFoundError si no existe
        user.change_role(new_role)
        return user
```

**Conceptos clave:**
- **Almacenamiento en memoria**: `dict[str, Usuario]` — suficiente para tests
- **Regla de negocio**: email duplicado → `BusinessRuleError`
- **Integración**: usa `Usuario.change_role()` que ya tiene su propia validación

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/idp/test_identity_service.py` | 12 | Creación (3), get_by_id (2), get_by_email (2), list_users (2), update_role (3) — incluye errores: duplicado, no encontrado |

```
73 passed in 0.71s  (incluye regresión de Sesiones 1-6)
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/idp/ports/identity_service_port.py` | Interfaz `IdentityServicePort` |
| `src/idp/adapters/mock/__init__.py` | Paquete mock |
| `src/idp/adapters/mock/identity_service_mock.py` | Mock en memoria |
| `tests/idp/test_identity_service.py` | 12 tests |

---

## Conclusión

Esta sesión completa el triángulo hexagonal del módulo IdP: **dominio** (`Usuario`, `UserId`, `UserRole`), **puerto** (`IdentityServicePort`) y **adapter** (`IdentityServiceMock`). La interfaz define qué se puede hacer con usuarios sin saber cómo se implementa — el mock demuestra que el contrato funciona con una implementación simple en memoria. Esto permite testear casos de uso y controladores sin necesidad de base de datos. La estructura está lista para que en Sesión 11 (Fase 5) se agregue un adapter SQLite sin cambiar ni una línea del dominio ni del puerto.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Tipo de interfaz | `ABC` | Nativo de Python, explícito, sin dependencias externas |
| Almacenamiento mock | `dict[str, Usuario]` | Simple, rápido, suficiente para tests |
| Validación de email duplicado | En el mock | Regla de negocio que aplica a cualquier adapter, pero implementada en cada uno |

---

## Próxima sesión

**Sesión 8: Historias de Usuario y Estimación Fibonacci** — Primera entidad del dominio Scrum.
