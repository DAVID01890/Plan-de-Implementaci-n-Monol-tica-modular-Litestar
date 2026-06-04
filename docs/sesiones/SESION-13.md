# Sesión 13 — Transactional Outbox

- **Fecha:** 2026-06-04
- **Fase:** 6 — Eventos y Consistencia Eventual
- **Estado:** ✅ Completada

---

## Objetivo

Implementar el patrón **Transactional Outbox**: persistir eventos de dominio en la misma transacción que el agregado, garantizando que nunca se pierdan. Crear un worker en background que procesa los eventos (poll + mark as processed).

**Criterio de éxito:** Tests que verifiquen que cada mutación del agregado genera eventos en la tabla `outbox_events`, y que el worker los procesa y marca como procesados.

---

## Implementación

### `src/scrum/domain/events.py` — Eventos de Dominio

Cinco eventos que registran cada mutación del agregado:

| Evento | Disparado por |
|--------|---------------|
| `ProyectoCreado` | `Proyecto.create()` |
| `HistoriaAgregada` | `Proyecto.add_historia()` |
| `SprintCreado` | `Proyecto.create_sprint()` |
| `SprintIniciado` | `Proyecto.start_sprint()` |
| `HistoriaAsignadaASprint` | `Proyecto.add_historia_to_sprint()` |

Cada evento extiende `DomainEvent` (con `event_id`, `occurred_at`, `event_type`) y tiene `to_dict()` para serialización JSON.

### `src/scrum/domain/entities.py` — Colección de Eventos en Proyecto

```python
class Proyecto:
    _domain_events: list[DomainEvent]

    def _register_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    @classmethod
    def create(cls, nombre: NotEmptyString) -> Proyecto:
        proyecto = cls(nombre=nombre)
        proyecto._register_event(ProyectoCreado(...))
        return proyecto
```

**Factory method vs constructor:** `__init__()` se usa también para reconstitución desde BD (sin eventos). `Proyecto.create()` es la fábrica para nuevas entidades y emite el evento de creación. Las mutaciones existentes (`add_historia`, `create_sprint`, etc.) registran su evento internamente.

`pull_domain_events()` retorna y limpia la lista. Es llamado por el repositorio después de guardar los datos.

### `src/db/schema.py` — Tabla outbox_events

```sql
CREATE TABLE IF NOT EXISTS outbox_events (
    id TEXT PRIMARY KEY,
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    processed_at TEXT,
    created_at TEXT NOT NULL
);
```

`processed_at` se setea cuando el worker procesa el evento. Eventos con `processed_at IS NULL` están pendientes.

### Integración en Repositorios

**SQLite** — En `ProyectoRepositorySQLite.save()`, después de escribir proyecto + sprints + historias, se insertan los eventos:

```python
events = proyecto.pull_domain_events()
for event in events:
    event_id, event_type, payload, occurred_at, created_at = serialize_event(event)
    await conn.execute(
        "INSERT INTO outbox_events (...) VALUES (?, ?, ?, ?, ?, ?)",
        (event_id, str(proyecto.id), event_type, payload, occurred_at, created_at),
    )
await conn.commit()
```

**Turso** — Misma lógica, pero agrega los INSERT al `batch()`:

```python
events = proyecto.pull_domain_events()
for event in events:
    stmts.append(("INSERT INTO outbox_events ...", (...)))
await client.batch(stmts)
```

La atomicidad es real en SQLite (misma conexión, misma transacción). En Turso, al ser HTTP batch, es atómica a nivel de un solo viaje (no hay transacción distribuida, pero es lo mejor que ofrece el protocolo).

### `src/scrum/infrastructure/outbox.py` — Serialización

```python
def serialize_event(event: DomainEvent) -> tuple[str, str, str, str, str]:
    return (event_id, event_type, payload_json, occurred_at_iso, created_at_iso)

def deserialize_event(event_id, event_type, payload, occurred_at) -> DomainEvent:
    ...
```

Mantiene un mapa `_EVENT_CLASSES` que asocia `event_type` strings a clases concretas, permitiendo reconstruir eventos desde la BD sin un switch manual.

### `src/scrum/infrastructure/outbox_worker.py` — Worker

```python
class OutboxWorker:
    async def _run_loop(self):
        while self._running:
            events = await self._client.get_unprocessed_events()
            for event in events:
                await self._handle_event(event.domain_event)
                await self._client.mark_as_processed(event.id)
            await asyncio.sleep(self._poll_interval)
```

Worker asíncrono que:
1. Cada 3 segundos consulta eventos no procesados
2. Deserializa cada evento a su clase de dominio
3. Ejecuta el handler (actualmente log-only)
4. Marca como procesado

### Integración en Lifespan de Litestar

```python
@asynccontextmanager
async def lifespan(app):
    await init_db()
    if is_turso_enabled():
        outbox_client = TursoOutboxClient(get_turso_client())
    else:
        outbox_client = SqliteOutboxClient(get_sqlite_connection())
    worker = OutboxWorker(outbox_client)
    await worker.start()
    yield
    await worker.stop()
```

El worker arranca con la app y se detiene al cerrar. Usa `SqliteOutboxClient` o `TursoOutboxClient` según entorno.

### `src/entrypoint/scrum/handlers.py` — Refactor de start_sprint

```python
# ❌ Antes: el handler llamaba a sprint.start() directamente,
#    el evento nunca se registraba en el agregado
sprint = proyecto.get_sprint(SprintId(sid))
sprint.start()

# ✅ Ahora: el agregado registra el evento internamente
proyecto.start_sprint(SprintId(sid))
```

El método `start_sprint()` en `Proyecto` llama a `sprint.start()` y luego registra `SprintIniciado`, garantizando que el worker pueda procesar este evento.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/scrum/test_outbox.py` | 18 | Serialización roundtrip (6), repo genera eventos (7), SQLiteOutboxClient (3), worker (2) |

```
200 passed, 1 skipped in 3.55s
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/scrum/domain/events.py` | 5 eventos de dominio con serialización |
| `src/scrum/infrastructure/__init__.py` | Paquete infrastructure |
| `src/scrum/infrastructure/outbox.py` | Serialización + `OutboxClient` abstracto + `OutboxEvent` dataclass |
| `src/scrum/infrastructure/outbox_sqlite.py` | `SqliteOutboxClient` — poll + mark processed |
| `src/scrum/infrastructure/outbox_turso.py` | `TursoOutboxClient` — poll + mark processed via batch |
| `src/scrum/infrastructure/outbox_worker.py` | `OutboxWorker` — background loop asíncrono |
| `tests/scrum/test_outbox.py` | 18 tests de integración |

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/db/schema.py` | + `outbox_events` table |
| `src/scrum/domain/entities.py` | + `_domain_events`, `pull_domain_events()`, `create()`, `start_sprint()`, eventos en mutaciones |
| `src/scrum/adapters/proyecto_repo_sqlite.py` | `save()` persiste outbox events |
| `src/scrum/adapters/proyecto_repo_turso.py` | `save()` persiste outbox events via batch |
| `src/entrypoint/app.py` | Lifespan arranca/para worker |
| `src/entrypoint/scrum/handlers.py` | `start_sprint` usa `proyecto.start_sprint()` |

---

## Conclusión

El patrón Transactional Outbox resuelve un problema fundamental de los sistemas basados en eventos: ¿cómo garantizar que el evento se publique si y solo si la transacción del agregado fue exitosa? La respuesta es escribirlos en la misma transacción.

En el ecosistema actual, los eventos se persisten en `outbox_events` pero **aún no tienen consumidores reales**. El worker actual solo registra en log. La siguiente fase (Sesión 14+) podría conectar estos eventos a un message broker, enviar notificaciones, o disparar proyecciones de CQRS. La infraestructura base está lista: cada mutación del agregado ya genera eventos, el outbox ya los persiste atómicamente, y el worker ya los procesa.

La decisión de refactorizar `start_sprint` del handler al agregado fue clave: el patrón solo funciona si todas las mutaciones pasan por el agregado. Si un handler modifica una entidad directamente, el evento nunca se registra.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Outbox en misma transacción | `INSERT` después del save del agregado | Atomicidad real (SQLite) o batch (Turso) |
| Factory method | `Proyecto.create()` vs `__init__()` | `__init__` se usa para reconstitución (sin eventos) |
| Worker polling | 3s de intervalo, configurable | Simple, sin dependencias externas (Redis, RabbitMQ) |
| OutboxClient abstracto | `SqliteOutboxClient` + `TursoOutboxClient` | Misma interfaz, diferentes backends |
| Handler refactorizado | `proyecto.start_sprint(sprint_id)` | El evento se registra dentro del agregado |

---

## Próxima sesión

**Sesión 14: La Tarea en Segundo Plano (Background Task)** — Conectar el worker a handlers reales: integración con servicios externos, proyecciones de CQRS, o envío de notificaciones.
