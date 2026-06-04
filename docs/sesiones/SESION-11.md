# Sesión 11 — Base de Datos Local y Migraciones

- **Fecha:** 2026-06-04
- **Fase:** 5 — Adaptadores de Persistencia
- **Estado:** ✅ Completada

---

## Objetivo

Configurar SQLite como base de datos local, Turso como base remota (producción), y Alembic para migraciones. Crear el esquema inicial con todas las tablas de las entidades de Scrum e IdP.

**Criterio de éxito:** Migraciones aplicadas correctamente con SQLite local, tablas creadas para proyectos, sprints, historias, tareas técnicas y usuarios.

---

## Implementación

### `src/db/connection.py` — Conexiones a BD

```python
def _db_path() -> str:
    return os.getenv("SQLITE_PATH", "local.db")

def _turso_url() -> str:
    return os.getenv("TURSO_DATABASE_URL", "")

def _turso_token() -> str:
    return os.getenv("TURSO_AUTH_TOKEN", "")
```

Tres funciones que leen variables de entorno **a tiempo de llamada**, no de importación. Esto permite tests que setean `SQLITE_PATH` dinámicamente sin conflictos. `is_turso_enabled()` retorna `True` solo si ambas variables `TURSO_DATABASE_URL` y `TURSO_AUTH_TOKEN` están presentes.

**¿Por qué funciones y no constantes?** Si fueran constantes de módulo, se evaluarían al importar el archivo. En tests que cambian `os.environ` después del import, las constantes quedarían desactualizadas. Al ser funciones, siempre leen el valor actual.

### SQLite vía `aiosqlite`

```python
@asynccontextmanager
async def get_sqlite_connection() -> AsyncIterator:
    async with aiosqlite.connect(_db_path()) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        yield conn
```

Usa `row_factory = aiosqlite.Row` para acceder a columnas por nombre (como `row["nombre"]`). WAL mode permite lecturas concurrentes sin bloqueos. `foreign_keys=ON` garantiza integridad referencial.

### Turso vía `libsql-client`

```python
@asynccontextmanager
async def get_turso_client() -> AsyncIterator:
    url = _turso_url().replace("libsql://", "https://", 1)
    client = create_client(url=url, auth_token=_turso_token())
    yield client
    await client.close()
```

Turso solo soporta HTTP (no WebSocket), por lo que la URL debe normalizarse de `libsql://` a `https://`.

### `src/db/schema.py` — CREATE TABLES

```sql
CREATE TABLE proyectos (id TEXT PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE sprints (id TEXT PRIMARY KEY, proyecto_id TEXT NOT NULL REFERENCES proyectos(id), ...);
CREATE TABLE historias (id TEXT PRIMARY KEY, proyecto_id TEXT NOT NULL REFERENCES proyectos(id), ...);
CREATE TABLE tareas_tecnicas (id TEXT PRIMARY KEY, historia_id TEXT NOT NULL REFERENCES historias(id), ...);
CREATE TABLE usuarios (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, ...);
```

Esquema plano en SQL, sin ORM. Cada tabla corresponde directamente a una entidad del dominio. `sprint_id` en `historias` refleja la relación many-to-one entre historias y sprints.

### Alembic

Dos migraciones:

| Migración | Descripción |
|-----------|-------------|
| `adb76cf28f92_initial_tables` | Tablas iniciales: proyectos, sprints, historias, tareas_tecnicas |
| `568d96a603d4_add_usuarios_table` | Agrega tabla `usuarios` |

`init_db()` ejecuta el CREATE_TABLES completo (CREATE IF NOT EXISTS), usado tanto en desarrollo como en tests.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/test_health.py` | 1 | Health endpoint funciona con BD inicializada |

```
163 passed in 1.50s
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/db/connection.py` | Conexiones asíncronas a SQLite y Turso |
| `src/db/schema.py` | DDL con CREATE TABLES de todas las entidades |
| `src/db/alembic.ini` | Configuración de Alembic |
| `src/db/migrations/` | Directorio de migraciones con env.py y script.py.mako |
| `src/db/migrations/versions/adb76cf28f92_initial_tables.py` | Migración inicial |
| `src/db/migrations/versions/568d96a603d4_add_usuarios_table.py` | Migración tabla usuarios |

---

## Conclusión

Esta sesión establece la capa de infraestructura de persistencia sin ORM. La decisión de usar SQL plano (`aiosqlite.execute`) en lugar de SQLAlchemy es deliberada: al no haber mapeo objeto-relacional, el código es explícito sobre qué SQL se ejecuta y cuándo. No hay magia de sesiones, no hay lazy loading, no hay N+1 queries ocultos.

La dualidad SQLite ↔ Turso prepara el proyecto para producción sin cambiar la interfaz: `init_db()`, `get_sqlite_connection()` y `get_turso_client()` son intercambiables según las variables de entorno. Los repositorios (Sesión 12) consumirán estas conexiones sin saber si están contra SQLite local o Turso remoto.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Sin ORM | SQL plano con `aiosqlite` | Control total del SQL, sin magic, sin N+1 |
| Conexiones vía env vars | Funciones (no constantes) | Evaluación tardía para tests |
| WAL mode | `PRAGMA journal_mode=WAL` | Lecturas concurrentes sin bloqueo |
| Turso URL normalizada | `libsql://` → `https://` | Turso no soporta WebSocket, solo HTTP |

---

## Próxima sesión

**Sesión 12: Repositorio Scrum (Guardar y Leer)** — Implementar adaptadores de persistencia para `ProyectoRepository`.
