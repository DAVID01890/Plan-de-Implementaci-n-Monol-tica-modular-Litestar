# Sesión 05 — Contratos de Eventos

- **Fecha:** 2026-06-03
- **Fase:** 2 — Shared Kernel (Dominio Base)
- **Estado:** ✅ Completada

---

## Objetivo

Definir la clase base para eventos de dominio (`DomainEvent`) en el Shared Kernel.

**Criterio de éxito:** Tests que verifiquen creación, inspección y comparación de eventos de dominio.

---

## Implementación

### `src/shared_kernel/domain/base_events.py` — DomainEvent

```python
from datetime import datetime, timezone

from src.shared_kernel.domain.base_value_objects import EntityId


class DomainEvent:
    def __init__(
        self,
        event_id: EntityId | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        self._event_id = event_id if event_id is not None else EntityId()
        self._occurred_at = (
            occurred_at if occurred_at is not None else datetime.now(timezone.utc)
        )

    @property
    def event_id(self) -> EntityId: ...

    @property
    def occurred_at(self) -> datetime: ...
```

**Conceptos clave:**
- **`event_id`**: `EntityId` único por evento, permite rastrear y referenciar eventos individualmente
- **`occurred_at`**: timestamp UTC con timezone-aware, se auto-asigna al crear el evento
- **Polimorfismo**: cualquier evento del dominio hereda de `DomainEvent` y se puede tratar como tal
- Sigue el mismo patrón de inmutabilidad y dunder methods que `EntityId`

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/shared_kernel/test_events.py` | 10 | Creación con defaults, UTC, IDs explícitos, igualdad, hash, string, repr, herencia |

```
47 passed in 0.62s  (incluye regresión de Sesiones 1-4)
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/shared_kernel/domain/base_events.py` | Clase base `DomainEvent` |
| `tests/shared_kernel/test_events.py` | 10 tests |

---

## Conclusión

`DomainEvent` cierra el triángulo base del Shared Kernel: ya tenemos **identidad** (`EntityId`), **validación** (`Email`, `NotEmptyString`, `PositiveInt` + `ValidationError`) y ahora **comunicación** (`DomainEvent`). Los eventos de dominio son el mecanismo por el cual el modelo notifica al mundo que algo relevante ocurrió (ej: "UsuarioCreado", "SprintIniciado"). Al tener una clase base con ID y timestamp, garantizamos que cada evento sea trazable y ordenable temporalmente desde el momento cero. Esto es la puerta de entrada a la Fase 6 (Transactional Outbox) y al patrón de consistencia eventual que vendrá más adelante.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Timestamp | UTC timezone-aware | Estándar para sistemas distribuidos, evita ambigüedad de zonas horarias |
| `event_id` como `EntityId` | Reutilización | Consistente con el resto del dominio |
| Parámetros opcionales | `event_id` y `occurred_at` opcionales | Facilita creación rápida, permite hidratación desde BD |

---

## Próxima sesión

**Sesión 6: Entidad Usuario y Objetos de Valor de Rol** — IdP: primera entidad real del dominio.
