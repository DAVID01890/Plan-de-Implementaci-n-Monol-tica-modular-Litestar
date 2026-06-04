# Sesión 12 — Repositorio Scrum (Guardar y Leer)

- **Fecha:** 2026-06-04
- **Fase:** 5 — Adaptadores de Persistencia
- **Estado:** ✅ Completada

---

## Objetivo

Implementar `ProyectoRepository` con dos adaptadores intercambiables: SQLite (local) y Turso (producción). Agregar `UsuarioRepository` SQLite para el módulo IdP. Crear los endpoints REST de Scrum que expongan toda la funcionalidad del agregado vía HTTP.

**Criterio de éxito:** Tests de integración que crean, guardan y recuperan proyectos completos (con sprints e historias) desde SQLite y Turso.

---

## Implementación

### `src/scrum/ports/proyecto_repository.py` — Puerto

```python
class ProyectoRepository(ABC):
    async def save(self, proyecto: Proyecto) -> None: ...
    async def find_by_id(self, proyecto_id: ProyectoId) -> Proyecto | None: ...
    async def delete(self, proyecto_id: ProyectoId) -> None: ...
    async def list(self) -> list[Proyecto]: ...
```

Puerto mínimo con cuatro operaciones. `save()` es upsert (INSERT OR REPLACE). `delete()` limpia en cascada (tareas → historias → sprints → proyecto).

### `src/scrum/adapters/proyecto_repo_sqlite.py` — Adaptador SQLite

```python
async def save(self, proyecto: Proyecto) -> None:
    async with get_sqlite_connection() as conn:
        await conn.execute("INSERT OR REPLACE INTO proyectos ...")
        for sprint in proyecto.sprints:
            await conn.execute("INSERT OR REPLACE INTO sprints ...")
        for historia in proyecto.historias:
            await conn.execute("INSERT OR REPLACE INTO historias ...")
        await conn.commit()
```

Cada `save()` abre una conexión, escribe proyecto + sprints + historias + backlog, y commitea. `find_by_id()` reconstruye el agregado completo con tres queries (proyecto, sprints, historias) y popula las referencias inversas (backlog de sprints).

**Principio:** El adaptador serializa/deserializa el agregado. No usa ORM — cada columna se mapea explícitamente a una propiedad del objeto de dominio.

### `src/scrum/adapters/proyecto_repo_turso.py` — Adaptador Turso

```python
async def save(self, proyecto: Proyecto) -> None:
    stmts = [...]
    client = create_client(url=self._url, auth_token=self._token)
    await client.batch(stmts)
    await client.close()
```

Turso no soporta transacciones SQL vía HTTP. En su lugar, usa `batch()` que ejecuta todas las sentencias en un solo viaje de ida y vuelta. No hay garantía atómica real (Turso no tiene transacciones HTTP), pero el batch es lo más cercano disponible.

### `src/idp/adapters/usuario_repo_sqlite.py` — Adaptador IdP

Mismo patrón que el repositorio Scrum, para `Usuario`. Cuatro operaciones: `save`, `find_by_id`, `find_by_email`, `list`, `delete`.

### Endpoints REST (`src/entrypoint/scrum/handlers.py` + `app.py`)

Nueve endpoints montados en Litestar vía `create_app()`:

| Método | Ruta | Handler |
|--------|------|---------|
| POST | `/proyectos` | `create_proyecto` |
| GET | `/proyectos` | `list_proyectos` |
| GET | `/proyectos/{id}` | `get_proyecto` |
| DELETE | `/proyectos/{id}` | `delete_proyecto` |
| POST | `/proyectos/{id}/historias` | `add_historia` |
| POST | `/proyectos/{id}/sprints` | `create_sprint` |
| POST | `/proyectos/{id}/sprints/historias` | `add_historia_to_sprint` |
| POST | `/proyectos/{id}/sprints/{sid}/start` | `start_sprint` |
| GET | `/health` | `health` |

**Inyección de dependencias:** Litestar resuelve `proyecto_repo` en los handlers vía la función `get_proyecto_repository()`, que selecciona el adaptador según `is_turso_enabled()`.

**Errores de dominio → HTTP:** `ValidationError` → 400, `NotFoundError` → 404, `BusinessRuleError` → 409.

### Problema Raíz: `yield` en DI

```python
# ❌ Original (roto):
async def get_proyecto_repository():
    yield ProyectoRepositorySQLite()

# ✅ Corregido:
async def get_proyecto_repository():
    return ProyectoRepositorySQLite()
```

Litestar 2.22 trata los generadores asíncronos (`async def` con `yield`) como *cleanup handlers*. Si la dependencia es un generador, Litestar descarta el valor retornado y devuelve `null` al cliente. Cambiar a `return` soluciona el problema.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/scrum/test_proyecto_repo_sqlite.py` | 3 | Save/find/delete con SQLite |
| `tests/scrum/test_proyecto_repo_turso.py` | 3 | Save/find/delete con Turso (skip si no hay credenciales) |
| `tests/idp/test_usuario_repo_sqlite.py` | 8 | CRUD completo de usuarios |
| `tests/test_proyecto_api.py` | 9 | Endpoints REST (create, get, delete, add_historia, create_sprint, start_sprint, etc.) |

```
182 passed, 1 skipped in 2.32s
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/scrum/ports/proyecto_repository.py` | Puerto abstracto ProyectoRepository |
| `src/scrum/adapters/proyecto_repo_sqlite.py` | Adaptador SQLite para Proyecto |
| `src/scrum/adapters/proyecto_repo_turso.py` | Adaptador Turso para Proyecto |
| `src/idp/ports/usuario_repository.py` | Puerto abstracto UsuarioRepository |
| `src/idp/adapters/usuario_repo_sqlite.py` | Adaptador SQLite para Usuario |
| `src/entrypoint/scrum/handlers.py` | 8 endpoints REST Scrum |
| `src/entrypoint/scrum/schemas.py` | Dataclasses request/response |
| `src/entrypoint/app.py` | Litestar app con DI y lifespan |
| `pyproject.toml` | Dependencias: litestar, aiosqlite, libsql-client, uvicorn |

---

## Conclusión

Esta sesión completa la capa de persistencia y la expone vía API REST. La arquitectura hexagonal se hace visible: los **puertos** (`ProyectoRepository`) definen el contrato, los **adaptadores** (`*SQLite`, `*Turso`) implementan la infraestructura, y los **handlers** HTTP son otro adaptador (entrada, no salida). El dominio (`Proyecto`, `Sprint`, `HistoriaDeUsuario`) no sabe de bases de datos ni de HTTP.

El bug del DI (`yield` vs `return`) fue una lección importante sobre cómo Litestar maneja los generadores asíncronos. La corrección fue simple pero crítica: sin ella, toda la API devolvía `null` en cada respuesta POST.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Repositorio intercambiable | Variable de entorno `TURSO_DATABASE_URL` | Mismo código, diferente BD según entorno |
| Turso sin transacciones | `batch()` en vez de `transaction()` | Turso HTTP no soporta transacciones |
| Serialización manual | SQL directo, sin ORM | Control total, cero magic |
| DI Litestar | `return` en vez de `yield` | yield causa null en Litestar 2.22 |
| Errores de dominio → HTTP | try/except con raise | Mapeo explícito, sin middleware genérico |

---

## Próxima sesión

**Sesión 13: Transactional Outbox** — Persistir eventos de dominio atómicamente con el agregado.
