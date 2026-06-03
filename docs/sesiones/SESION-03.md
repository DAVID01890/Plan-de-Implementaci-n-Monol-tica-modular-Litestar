# Sesión 03 — Identificadores Únicos y Excepciones

- **Fecha:** 2026-06-03
- **Fase:** 2 — Shared Kernel (Dominio Base)
- **Estado:** ✅ Completada

---

## Objetivo

Crear las bases del Shared Kernel: el Value Object `EntityId` (UUID v4) y la jerarquía de excepciones del dominio.

**Criterio de éxito:** 12 tests unitarios pasando.

---

## Implementación

### `src/shared_kernel/domain/base_value_objects.py` — `EntityId`

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

**Conceptos clave:**
- **Value Object DDD**: inmutable, se compara por valor (`__eq__`), usable como clave (`__hash__`)
- **UUID v4 opcional**: si no se pasa valor, genera uno nuevo; si se pasa, lo reusa (útil al hidratar desde BD)
- **`NotImplemented` en `__eq__`**: sigue el protocolo Python, permite comparación inversa entre tipos
- **`__class__.__name__`** en `__repr__`: permite herencia sin hardcodear el nombre de la clase

### `src/shared_kernel/domain/base_exceptions.py` — Jerarquía de excepciones

```python
class DomainError(Exception): ...

class NotFoundError(DomainError):
    # Almacena entity_name + entity_id, mensaje formateado automáticamente

class ValidationError(DomainError): ...

class BusinessRuleError(DomainError): ...
```

```
Exception
 └── DomainError
      ├── NotFoundError      ← "User with id '123' not found"
      ├── ValidationError    ← valor inválido
      └── BusinessRuleError  ← regla de negocio violada
```

**¿Por qué no `ValueError` de Python?** Porque `except DomainError` captura solo errores de negocio, sin mezclarlos con errores técnicos (`KeyError`, `TypeError`). Además cada subtipo puede llevar metadata estructurada.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/shared_kernel/test_value_objects.py` | 7 | Creación de UUID, igualdad, hash, string y repr |
| `tests/shared_kernel/test_exceptions.py` | 5 | Herencia, formato de mensaje, polimorfismo (`except DomainError`) |

```
13 passed in 0.90s  (incluye test de salud de Sesión 2 — sin regresión)
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/shared_kernel/domain/base_value_objects.py` | `EntityId` (UUID v4) |
| `src/shared_kernel/domain/base_exceptions.py` | `DomainError`, `NotFoundError`, `ValidationError`, `BusinessRuleError` |
| `tests/shared_kernel/__init__.py` | Paquete de tests |
| `tests/shared_kernel/test_value_objects.py` | 7 tests |
| `tests/shared_kernel/test_exceptions.py` | 5 tests |

---

## Conclusión

Esta sesión construyó el primer piso del dominio compartido. `EntityId` no es solo un UUID con wrapper: es el contrato que usarán todas las entidades del sistema (Usuario, Proyecto, Sprint, Historia de Usuario) para garantizar identidad, comparabilidad y capacidad de persistencia desde el día cero. La jerarquía de excepciones, por su parte, establece un lenguaje ubícuo para los errores de negocio: quien recibe un `NotFoundError` sabe exactamente qué entidad falta y por qué, mientras que un `BusinessRuleError` comunica una violación de reglas sin ambigüedad. Ambos componentes son la base sobre la que se sostendrá todo el dominio de IdP y Scrum en las sesiones siguientes. Doce tests verifican que estos cimientos sean sólidos.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Tipo de ID | UUID v4 | Sin coordinación central, suficiente para PoC |
| Inmutabilidad | Sin setters | Value Objects inmutables por definición DDD |
| Jerarquía de excepciones | 3 subtipos + base | Granularidad sin complejidad excesiva |

---

## Próxima sesión

**Sesión 4: Tipos Primitivos (Objetos de Valor Genéricos)** — `Email`, `NotEmptyString`, `PositiveInt`.
