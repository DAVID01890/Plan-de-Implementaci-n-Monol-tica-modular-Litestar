# ▶️ Próxima Sesión — Handoff

## Sesión 14: Handlers Reales del Outbox (Integración)

**Objetivo:** Conectar el worker del outbox a handlers reales: enviar eventos a un webhook externo, actualizar proyecciones de lectura (CQRS), o enviar notificaciones.

**Criterio de éxito:** Eventos del outbox disparan acciones concretas (ej. log estructurado, webhook HTTP, actualización de tabla de proyección).

## Estado actual del proyecto

- ✅ Sesión 1-9: Estructura, Shared Kernel, IdP, Scrum domain
- ✅ Sesión 10: `Proyecto` aggregate, `Sprint`, exclusividad temporal
- ✅ Sesión 11: `connection.py`, `schema.py`, Alembic migraciones
- ✅ Sesión 12: Repositorios SQLite + Turso, API REST (9 endpoints), DI Litestar
- ✅ Sesión 13: Transactional Outbox (eventos, tabla, insert atómico, worker background)
- Suite: **200 tests passing, 1 skipped** (Turso sin credenciales)

## Contexto relevante

- El worker (`OutboxWorker`) ya corre en el lifespan de Litestar
- Actualmente el handler es no-op (solo log)
- El outbox persiste 5 tipos de evento: `proyecto.creado`, `proyecto.historia.agregada`, `proyecto.sprint.creado`, `proyecto.sprint.iniciado`, `proyecto.sprint.historia_asignada`
- Cada evento tiene `to_dict()` para serialización JSON
- `OutboxClient` abstracto con impls SQLite y Turso

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
.venv\Scripts\pytest -v
python -m uvicorn src.entrypoint.app:create_app --factory --host 127.0.0.1 --port 8000
```
