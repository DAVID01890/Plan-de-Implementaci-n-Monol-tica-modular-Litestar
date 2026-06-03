# Sesión 06 — Entidad Usuario y Objetos de Valor de Rol

- **Fecha:** 2026-06-03
- **Fase:** 3 — Proveedor de Identidad (IdP — Dominio y Puerto)
- **Estado:** ✅ Completada

---

## Objetivo

Crear la primera entidad del dominio IdP: `Usuario` con sus Value Objects (`UserId`, `UserRole`) y reglas de negocio asociadas.

**Criterio de éxito:** Tests que verifiquen creación, activación/desactivación, cambio de rol y comparación de usuarios.

---

## Implementación

### `src/idp/domain/value_objects.py` — UserId, UserRole

```python
class UserId(EntityId):
    pass


class UserRole(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
```

**Conceptos clave:**
- `UserId` hereda de `EntityId` (UUID v4) sin añadir nada — el type hint evita confundir IDs de distintas entidades
- `UserRole` es un `Enum` con tres valores: `ADMIN`, `DEVELOPER`, `VIEWER`

### `src/idp/domain/entities.py` — Usuario

```python
class Usuario:
    def __init__(
        self,
        email: Email,
        name: NotEmptyString,
        role: UserRole = UserRole.DEVELOPER,
        id: UserId | None = None,
        is_active: bool = True,
    ) -> None: ...

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
            raise BusinessRuleError(f"User already has role '{new_role.value}'")
        self._role = new_role
```

**Conceptos clave:**
- **Entidad DDD**: se identifica por su `id` (UserId), no por sus atributos — dos usuarios con mismo email y nombre pero distinto ID son distintos
- **Reglas de negocio**: `activate()`/`deactivate()` son transiciones de estado con guardas que lanzan `BusinessRuleError`
- **Value Objects reutilizados**: `Email` y `NotEmptyString` del Shared Kernel garantizan validación sin repetir lógica
- **Rol por defecto**: `DEVELOPER` — el rol más común en un equipo Scrum

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/idp/test_usuario.py` | 14 | Creación (defaults, role explícito, ID explícito), activación/desactivación (4 tests, incluyendo errores), cambio de rol (2 tests), igualdad (3 tests), string/repr (2 tests) |

```
61 passed in 0.71s  (incluye regresión de Sesiones 1-5)
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/idp/domain/value_objects.py` | `UserId` (hereda de `EntityId`), `UserRole` (enum) |
| `src/idp/domain/entities.py` | `Usuario` con reglas de negocio |
| `tests/idp/__init__.py` | Paquete de tests |
| `tests/idp/test_usuario.py` | 14 tests |

---

## Conclusión

`Usuario` es la primera entidad real del proyecto y marca la transición del Shared Kernel (genérico) al dominio concreto de IdP. La entidad demuestra el valor de las sesiones anteriores: `UserId` hereda de `EntityId` (Sesión 3), `Email` y `NotEmptyString` validan solos (Sesión 4), y `BusinessRuleError` da semántica a las reglas de negocio (Sesión 3). El diseño refleja DDD puro: el usuario no es un simple contenedor de datos, sino un agregado con comportamiento —sabe activarse, desactivarse y cambiar de rol, y rechaza transiciones inválidas con errores explícitos—.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| `UserId` como subclase vs alias | Subclase de `EntityId` | Type safety: una función que espera `UserId` no acepta un `EntityId` genérico |
| Rol por defecto | `DEVELOPER` | Perfil más común en Scrum; evita obligar a pasarlo siempre |
| `is_active` booleano | `True` por defecto | Asume que un usuario recién creado está activo |

---

## Próxima sesión

**Sesión 7: El Puerto IdentityServicePort (Interfaz y Mock)** — Contrato para operaciones sobre usuarios y su implementación de prueba.
