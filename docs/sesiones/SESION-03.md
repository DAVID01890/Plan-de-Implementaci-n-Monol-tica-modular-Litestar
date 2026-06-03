# Sesión 03 — Identificadores Únicos y Excepciones

- **Fecha:** 2026-06-03
- **Fase:** 2 — Shared Kernel (Dominio Base)
- **Estado:** ✅ Completada

---

## Objetivo

Crear las bases del Shared Kernel: objetos de valor genéricos (`EntityId`) y manejo de excepciones del dominio (`DomainError`, `NotFoundError`, `ValidationError`, `BusinessRuleError`).

**Criterio de éxito:** Tests que verifiquen la creación de IDs únicos (UUID) y excepciones base del dominio.

---

## Paso a paso

### 1. Revisión del estado del proyecto

Antes de empezar se ejecutó:

```
git log --oneline -5
git status
```

El proyecto tenía:
- Sesión 1 ✅: estructura hexagonal vacía con `__init__.py` en todos los paquetes
- Sesión 2 ✅: `src/entrypoint/app.py` con `GET /health` y su test
- `src/shared_kernel/domain/` — solo un `__init__.py` vacío
- `tests/` — solo `test_health.py`

### 2. Lectura del handoff (PROXIMA-SESION.md)

Se confirmaron las instrucciones:
- Crear `src/shared_kernel/domain/base_value_objects.py` con `EntityId` (UUID v4)
- Crear `src/shared_kernel/domain/base_exceptions.py` con `DomainError` y subtipos
- Tests en `tests/shared_kernel/`

---

## Implementación detallada

### 3. `src/shared_kernel/domain/base_value_objects.py`

```python
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
```

**Explicación línea por línea:**

| Línea | Descripción |
|-------|-------------|
| `from __future__ import annotations` | Activa evaluación diferida de anotaciones de tipo (PEP 563). Permite usar `UUID \| None` sin importar `Optional`. Estándar en proyectos modernos Python 3.7+. |
| `from uuid import UUID, uuid4` | `UUID` es el tipo nativo de Python para UUIDs. `uuid4()` genera un UUID aleatorio (versión 4). |
| `class EntityId:` | Clase que representa un identificador único de entidad. Es un **objeto de valor (Value Object)** — inmutable, se compara por valor, no por identidad de objeto. |
| `_value: UUID` | Atributo privado con type hint. El guion bajo indica que es de uso interno. Almacena el UUID real. |
| `def __init__(self, value: UUID \| None = None) -> None:` | Constructor. Acepta un UUID opcional. Si no se pasa (None), genera uno nuevo con `uuid4()`. Esto permite recrear IDs desde persistencia (ej. base de datos) pasando el UUID existente. |
| `self._value = value if value is not None else uuid4()` | Asigna el valor. Si `value` es `None`, genera un UUID v4 aleatorio. El operador ternario evita un bloque `if` separado. |
| `@property` | Decorador que convierte el método en propiedad de solo lectura. Así `entity_id.value` se usa como atributo, no como método. |
| `def value(self) -> UUID:` | Getter público. Retorna el UUID interno. No hay setter — el objeto es inmutable una vez creado. |
| `def __eq__(self, other: object) -> bool:` | Dunder method para `==`. Compara dos `EntityId` por su valor interno, no por referencia de objeto. |
| `if not isinstance(other, EntityId): return NotImplemented` | Si `other` no es un `EntityId`, retorna `NotImplemented` para que Python intente la comparación inversa. Evita `TypeError`. |
| `return self._value == other._value` | Compara los UUIDs internos. Dos `EntityId` son iguales si envuelven el mismo UUID. |
| `def __hash__(self) -> int:` | Dunder method para `hash()`. Necesario si se usan `EntityId` como claves en `dict` o elementos en `set`. |
| `return hash(self._value)` | Delega el hash al UUID interno. Garantiza que dos `EntityId` iguales tengan el mismo hash. |
| `def __str__(self) -> str:` | Dunder method para `str()`. Devuelve la representación en string del UUID (ej. `"550e8400-e29b-41d4-a716-446655440000"`). |
| `def __repr__(self) -> str:` | Dunder method para `repr()`. Devuelve una representación que idealmente permite recrear el objeto (ej. `EntityId(550e8400-e29b-41d4-a716-446655440000)`). |
| `f"{self.__class__.__name__}({str(self._value)})"` | Usa `__class__.__name__` en lugar de hardcodear `"EntityId"` para que funcione correctamente si se hereda. |

**Decisiones técnicas:**

| Decisión | Opción | Razón |
|----------|--------|-------|
| Tipo de UUID | UUID v4 (aleatorio) | No requiere coordinación centralizada, suficiente para PoC. En producción podría usarse v7 (orden temporal). |
| Inmutabilidad | Sin setters, asignación solo en `__init__` | Los Value Objects deben ser inmutables por definición (DDD). |
| `NotImplemented` en `__eq__` vs `return False` | `NotImplemented` | Sigue el protocolo de Python: permite que `other.__eq__` tenga oportunidad de responder. |

---

### 4. `src/shared_kernel/domain/base_exceptions.py`

```python
from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    """Raised when an entity is not found."""

    def __init__(self, entity_name: str, entity_id: str) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id '{entity_id}' not found")


class ValidationError(DomainError):
    """Raised when domain validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BusinessRuleError(DomainError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
```

**Explicación línea por línea:**

| Línea | Descripción |
|-------|-------------|
| `class DomainError(Exception):` | Clase base para **todas** las excepciones del dominio. Hereda de `Exception` directamente. Al tener esta clase base, los casos de uso pueden atrapar cualquier error de dominio con un solo `except DomainError`. |
| `def __init__(self, message: str) -> None:` | Constructor que acepta un mensaje descriptivo. |
| `self.message = message` | Almacena el mensaje como atributo para acceso programático. |
| `super().__init__(message)` | Pasa el mensaje a `Exception.__init__` para que `str(error)` funcione correctamente. |
| `class NotFoundError(DomainError):` | Error semántico: "no encontré la entidad". Lleva información estructurada: nombre de la entidad y su ID. |
| `def __init__(self, entity_name: str, entity_id: str) -> None:` | Acepta dos parámetros en lugar de un mensaje genérico. Esto fuerza a quien lanza la excepción a proporcionar datos específicos. |
| `super().__init__(f"...")` | Construye el mensaje automáticamente con formato: `"User with id '123' not found"`. Esto mantiene mensajes consistentes en todo el dominio. |
| `class ValidationError(DomainError):` | Error semántico: "el valor no pasó validación". Ej: email inválido, nombre vacío. No añade atributos extra porque el mensaje es suficiente. |
| `class BusinessRuleError(DomainError):` | Error semántico: "se violó una regla de negocio". Ej: "no se puede cerrar un sprint con tareas abiertas". Distinto de `ValidationError` porque la regla involucra el estado del sistema, no un valor individual. |

**Jerarquía resultante:**
```
Exception
 └── DomainError          ← base del dominio
      ├── NotFoundError    ← entidad no encontrada
      ├── ValidationError  ← validación fallida
      └── BusinessRuleError ← regla de negocio violada
```

**¿Por qué tres subtipos y no solo `DomainError`?**

| Subtipo | Uso típico | Ejemplo |
|---------|------------|---------|
| `NotFoundError` | Repositorios, casos de uso que buscan entidades | `raise NotFoundError("User", user_id)` |
| `ValidationError` | Fábricas, constructores de Value Objects | `raise ValidationError("Email must contain @")` |
| `BusinessRuleError` | Agregados, servicios de dominio | `raise BusinessRuleError("Cannot archive active sprint")` |

**¿Por qué no usar `ValueError` de Python?**

`ValueError` es genérico y no distingue entre errores de dominio y errores técnicos. Al tener nuestra propia jerarquía:
- Los casos de uso pueden atrapar `DomainError` sin atrapar errores del runtime (ej. `KeyError`, `TypeError`)
- Se puede añadir metadata a cada tipo sin romper APIs
- La intención del error es explícita en el nombre de la clase

---

### 5. Tests

#### `tests/shared_kernel/test_value_objects.py`

```python
from uuid import UUID, uuid4

from src.shared_kernel.domain.base_value_objects import EntityId


def test_entity_id_generates_uuid_on_creation() -> None:
    entity_id = EntityId()
    assert isinstance(entity_id.value, UUID)


def test_entity_id_accepts_explicit_uuid() -> None:
    uid = uuid4()
    entity_id = EntityId(value=uid)
    assert entity_id.value == uid


def test_entity_id_equality() -> None:
    uid = uuid4()
    id1 = EntityId(value=uid)
    id2 = EntityId(value=uid)
    assert id1 == id2


def test_entity_id_inequality() -> None:
    id1 = EntityId()
    id2 = EntityId()
    assert id1 != id2


def test_entity_id_hash() -> None:
    uid = uuid4()
    id1 = EntityId(value=uid)
    id2 = EntityId(value=uid)
    assert hash(id1) == hash(id2)


def test_entity_id_str_representation() -> None:
    uid = uuid4()
    entity_id = EntityId(value=uid)
    assert str(entity_id) == str(uid)


def test_entity_id_repr() -> None:
    uid = uuid4()
    entity_id = EntityId(value=uid)
    assert repr(entity_id) == f"EntityId({str(uid)})"
```

**Explicación de cada test:**

| Test | ¿Qué verifica? | ¿Por qué es importante? |
|------|----------------|------------------------|
| `test_entity_id_generates_uuid_on_creation` | Que al crear `EntityId()` sin argumentos se genera un UUID automáticamente | Garantiza que el comportamiento por defecto funciona y que el valor es un tipo `UUID` real |
| `test_entity_id_accepts_explicit_uuid` | Que se puede pasar un UUID existente y se conserva | Necesario para reconstruir IDs desde base de datos (hidratación) |
| `test_entity_id_equality` | Que dos instancias con el mismo UUID son iguales (`==`) | Esencial para comparar entidades sin comparar referencias de objeto |
| `test_entity_id_inequality` | Que dos instancias con diferente UUID son distintas | Dos entidades distintas nunca deben ser iguales |
| `test_entity_id_hash` | Que dos instancias iguales tienen el mismo hash | Necesario para usar `EntityId` como clave en `dict` o elemento en `set` |
| `test_entity_id_str_representation` | Que `str(entity_id)` devuelve el UUID como string | Útil para logging, respuestas HTTP, debugging |
| `test_entity_id_repr` | Que `repr(entity_id)` devuelve una representación descriptiva | Útil en depuración interactiva (REPL, consola) |

#### `tests/shared_kernel/test_exceptions.py`

```python
import pytest

from src.shared_kernel.domain.base_exceptions import (
    BusinessRuleError,
    DomainError,
    NotFoundError,
    ValidationError,
)


def test_domain_error_is_exception() -> None:
    error = DomainError("something went wrong")
    assert isinstance(error, Exception)
    assert str(error) == "something went wrong"
    assert error.message == "something went wrong"


def test_not_found_error_format() -> None:
    error = NotFoundError(entity_name="User", entity_id="123")
    assert isinstance(error, DomainError)
    assert str(error) == "User with id '123' not found"
    assert error.entity_name == "User"
    assert error.entity_id == "123"


def test_validation_error() -> None:
    error = ValidationError("invalid email")
    assert isinstance(error, DomainError)
    assert str(error) == "invalid email"


def test_business_rule_error() -> None:
    error = BusinessRuleError("sprint cannot be closed with open tasks")
    assert isinstance(error, DomainError)
    assert str(error) == "sprint cannot be closed with open tasks"


def test_all_errors_can_be_caught_as_domain_error() -> None:
    errors: list[DomainError] = [
        NotFoundError("Project", "1"),
        ValidationError("bad value"),
        BusinessRuleError("rule broken"),
    ]
    for error in errors:
        with pytest.raises(DomainError):
            raise error
```

**Explicación de cada test:**

| Test | ¿Qué verifica? | ¿Por qué es importante? |
|------|----------------|------------------------|
| `test_domain_error_is_exception` | Que `DomainError` es una `Exception` real y que `message` se almacena correctamente | Confirma la herencia base y que `str(error)` funciona |
| `test_not_found_error_format` | Que `NotFoundError` almacena `entity_name` y `entity_id`, y genera el mensaje formateado | Garantiza mensajes consistentes en todo el dominio |
| `test_validation_error` | Que `ValidationError` es un `DomainError` | Confirma la herencia y que el mensaje se pasa correctamente |
| `test_business_rule_error` | Que `BusinessRuleError` es un `DomainError` | Ídem |
| `test_all_errors_can_be_caught_as_domain_error` | Que todos los subtipos son atrapables con `except DomainError` | Es la razón de ser de la jerarquía: un solo catch para todos los errores de dominio |

---

### 6. Ejecución de tests

```
uv run pytest -v
```

```
tests\shared_kernel\test_exceptions.py::test_domain_error_is_exception PASSED [  7%]
tests\shared_kernel\test_exceptions.py::test_not_found_error_format PASSED [ 15%]
tests\shared_kernel\test_exceptions.py::test_validation_error PASSED     [ 23%]
tests\shared_kernel\test_exceptions.py::test_business_rule_error PASSED  [ 30%]
tests\shared_kernel\test_exceptions.py::test_all_errors_can_be_caught_as_domain_error PASSED [ 38%]
tests\shared_kernel\test_value_objects.py::test_entity_id_generates_uuid_on_creation PASSED [ 46%]
tests\shared_kernel\test_value_objects.py::test_entity_id_accepts_explicit_uuid PASSED [ 53%]
tests\shared_kernel\test_value_objects.py::test_entity_id_equality PASSED [ 61%]
tests\shared_kernel\test_value_objects.py::test_entity_id_inequality PASSED [ 69%]
tests\shared_kernel\test_value_objects.py::test_entity_id_hash PASSED    [ 76%]
tests\shared_kernel\test_value_objects.py::test_entity_id_str_representation PASSED [ 84%]
tests\shared_kernel\test_value_objects.py::test_entity_id_repr PASSED    [ 92%]
tests\test_health.py::test_health_returns_200 PASSED                     [100%]

13 passed in 0.90s
```

**Nota:** Todos los tests pasan, incluido `test_health_returns_200` de la Sesión 2 (regresión). Esto confirma que no se rompió nada existente.

---

## Archivos creados/modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/shared_kernel/domain/base_value_objects.py` | ✅ Creado | Clase `EntityId` (UUID v4) |
| `src/shared_kernel/domain/base_exceptions.py` | ✅ Creado | Jerarquía de excepciones de dominio |
| `tests/shared_kernel/__init__.py` | ✅ Creado | Paquete de tests (vacío) |
| `tests/shared_kernel/test_value_objects.py` | ✅ Creado | 7 tests para `EntityId` |
| `tests/shared_kernel/test_exceptions.py` | ✅ Creado | 5 tests para excepciones |
| `docs/AVANCE.md` | 📝 Modificado | Sesión 3 marcada como ✅, fecha actualizada |
| `docs/PROXIMA-SESION.md` | 📝 Modificado | Handoff actualizado a Sesión 4 |
| `docs/sesiones/SESION-03.md` | ✅ Creado | Bitácora detallada (este archivo) |

---

## Estado del proyecto al cierre

- Working tree limpio (`git status`)
- Último commit: `b40e79e` — `feat: add EntityId and domain exceptions (Session 3)`
- 13 tests pasando (7 nuevos + 5 nuevos + 1 existente)
- Shared Kernel ya tiene sus primeras clases funcionales

```
src/
  shared_kernel/
    domain/
      __init__.py
      base_value_objects.py    ← NUEVO: EntityId
      base_exceptions.py       ← NUEVO: DomainError y subtipos
    ports/
      __init__.py
  idp/ ...
  scrum/ ...
  entrypoint/
    app.py                     ← Health check (Sesión 2)
tests/
  __init__.py
  test_health.py               ← Health check test (Sesión 2)
  shared_kernel/
    __init__.py                 ← NUEVO
    test_value_objects.py       ← NUEVO
    test_exceptions.py          ← NUEVO
```

---

## Conclusión

**¿Qué?** Se crearon las bases del Shared Kernel: el Value Object `EntityId` (UUID v4) y la jerarquía de excepciones del dominio (`DomainError`, `NotFoundError`, `ValidationError`, `BusinessRuleError`).

**¿Por qué?** `EntityId` es el bloque fundamental de cualquier entidad DDD — todas las entidades del dominio (Usuario, Proyecto, Sprint, Historia de Usuario) heredarán de él. Las excepciones de dominio permiten que los casos de uso atrapen errores de negocio con un solo `except DomainError` sin mezclarlos con errores técnicos (`KeyError`, `TypeError`, etc.).

**¿Cómo?** `EntityId` envuelve un `UUID` nativo de Python, es inmutable, comparable por valor y usable como clave en diccionarios. La jerarquía de excepciones hereda de `Exception` con tres subtipos semánticos que contienen metadata estructurada (`entity_name`, `entity_id`). Todo validado con 12 tests unitarios.

## Comandos ejecutados en esta sesión

```powershell
# Ver historial y estado
git log --oneline -5
git status

# Ejecutar tests
uv run pytest -v

# Commit final
git add -A
git commit -m "feat: add EntityId and domain exceptions (Session 3)"
```

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Tipo de ID | UUID v4 | Sin coordinación central, suficiente para PoC |
| Inmutabilidad | Sin setters | Los Value Objects son inmutables por definición (DDD) |
| `__eq__` con `NotImplemented` | Seguir protocolo Python | Permite comparación inversa entre tipos |
| Jerarquía de excepciones | 3 subtipos + base | Balance entre granularidad y simplicidad |
| `from __future__ import annotations` | Sí | Evaluación diferida de tipos, estándar moderno |

---

## Próxima sesión

**Sesión 4: Tipos Primitivos (Objetos de Valor Genéricos)** — `Email`, `NotEmptyString`, `PositiveInt` en el Shared Kernel.
