# Sesión 14 — Handlers Reales del Outbox (Integración)

- **Fecha:** 2026-06-05
- **Fase:** 6 — Eventos y Consistencia Eventual (Transactional Outbox)
- **Estado:** ✅ Completada

---

## Objetivo

Conectar el worker del outbox a handlers reales que ejecuten side-effects concretos: log estructurado, proyección CQRS (read model), y webhook HTTP.

**Criterio de éxito:** Cada evento del outbox dispara 1) un log JSON estructurado, 2) una actualización en la tabla `proyecto_read_model`, y 3) opcionalmente un POST HTTP a una URL configurable.

---

## Implementación

### `src/scrum/infrastructure/outbox_handlers.py` — Handler interface + 3 implementaciones

```python
class OutboxEventHandler(ABC):
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None: ...
```

Tres implementaciones:

| Handler | Qué hace | Configuración |
|---------|----------|---------------|
| `LoggingHandler` | Log INFO con `event_type` + `to_dict()` | Siempre activo |
| `WebhookHandler` | POST HTTP con payload JSON del evento | `OUTBOX_WEBHOOK_URL` |
| `ProjectionHandler` | UPDATE/INSERT en `proyecto_read_model` | Solo SQLite |

El `ProjectionHandler` mantiene una tabla desnormalizada (`proyecto_read_model`) que acumula:
- `total_historias` y `total_story_points` (se incrementan con cada `HistoriaAgregada`)
- `sprint_actual_id` (se actualiza con cada `SprintIniciado`)

### `src/scrum/infrastructure/outbox_worker.py` — Worker ahora acepta handlers

```python
class OutboxWorker:
    def __init__(self, client, poll_interval=3.0, handlers=None):
        self._handlers = handlers or []
```

Cada evento se pasa por todos los handlers; si uno falla, se loguea el error pero no se interrumpe el batch.

### `src/entrypoint/app.py` — Wiring en el lifespan

```python
handlers = [LoggingHandler()]
if webhook_url:
    handlers.append(WebhookHandler(webhook_url))
if not is_turso_enabled():
    handlers.append(ProjectionHandler(conn))
```

### `src/db/schema.py` — Nueva tabla de proyección

```sql
CREATE TABLE IF NOT EXISTS proyecto_read_model (
    proyecto_id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    total_historias INTEGER NOT NULL DEFAULT 0,
    total_story_points INTEGER NOT NULL DEFAULT 0,
    sprint_actual_id TEXT,
    sprint_actual_nombre TEXT,
    updated_at TEXT NOT NULL
);
```

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/scrum/test_outbox_handlers.py` | 10 | LoggingHandler, WebhookHandler (skip sin respx), ProjectionHandler (5 eventos), worker con handlers, tolerancia a fallos |
| `tests/scrum/test_outbox.py` | 17 | Regresión: serialización, generación de eventos, outbox client |

```
Resultado: 212 passed, 1 skipped en 14.91s
```

---

## Archivos creados/modificados

| Archivo | Cambio |
|---------|--------|
| `src/scrum/infrastructure/outbox_handlers.py` | ✨ Creado — Handler interface + 3 implementaciones |
| `src/scrum/infrastructure/outbox_worker.py` | 🔄 Modificado — Acepta `handlers` list, los llama en `_handle_event` |
| `src/db/schema.py` | 🔄 Modificado — Agregada `proyecto_read_model` |
| `src/entrypoint/app.py` | 🔄 Modificado — Wiring de handlers en lifespan |
| `requirements.txt` | 🔄 Modificado — Agregado `httpx>=0.28` |
| `tests/scrum/test_outbox_handlers.py` | ✨ Creado — 10 tests de handlers |
| `docs/PROXIMA-SESION.md` | 🔄 Actualizado — Avance a Sesión 15 |
| `docs/AVANCE.md` | 🔄 Actualizado |

---

## Conclusión

Esta sesión cierra el ciclo del Transactional Outbox: los eventos ya no se pierden en un no-op, sino que producen side-effects medibles. El `LoggingHandler` da observabilidad inmediata, el `ProjectionHandler` habilita consultas de lectura livianas (CQRS básico sin cambiar la arquitectura), y el `WebhookHandler` deja la puerta abierta a integraciones externas (Slack, CI, etc.).

La tabla `proyecto_read_model` es particularmente estratégica: al mantener counts agregados en una fila por proyecto, las consultas de listado (`GET /proyectos`) podrían servirse desde esta tabla en lugar de hacer JOINs contra 3 tablas. Esta optimización queda para una sesión futura.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Handler interface vs callbacks | ABC con `handle()` | Tipado explícito, extensible, testeable |
| `ProjectionHandler` solo para SQLite | No implementar en Turso | El `aiosqlite.Connection` es compartido; Turso requeriría otro patrón de conexión. Fácil de añadir después. |
| `to_dict()` para acceso a datos | No usar properties privadas | Los eventos exponen `to_dict()` públicamente; acceder a `_story_points` violaría encapsulamiento |
| httpx para webhook | Dependencia externa | Ya estaba en el árbol de dependencias vía Litestar; cliente HTTP async maduro |

---

## Próxima sesión

**Sesión 15: Configuración de Plugins y Variables de Entorno** — Litestar plugins, gestión de configuración centralizada, y limpieza de deprecation warnings en path parameters.
