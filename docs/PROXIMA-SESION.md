# ▶️ Próxima Sesión — Handoff

## Sesión 20: Optimización y Performance

**Objetivo:** Connection pooling, caching de consultas frecuentes, y profiling básico.

**Criterio de éxito:** Reducción de latencia en endpoints críticos; conexiones a DB reutilizadas.

## Estado actual del proyecto

- ✅ Sesión 1–9: Estructura, Shared Kernel, IdP, Scrum domain
- ✅ Sesión 10: `Proyecto` aggregate, `Sprint`, exclusividad temporal
- ✅ Sesión 11: `connection.py`, `schema.py`, Alembic migraciones
- ✅ Sesión 12: Repositorios SQLite + Turso, API REST (9 endpoints), DI Litestar
- ✅ Sesión 13: Transactional Outbox (eventos, tabla, insert atómico, worker background)
- ✅ Sesión 14: Handlers reales del outbox (LoggingHandler, WebhookHandler, ProjectionHandler)
- ✅ Sesión 15: Configuración centralizada (Settings dataclass, plugins Litestar, eliminar deprecation warnings)
- ✅ Sesión 16: Controladores HTTP (ProyectoController) + RequestLoggingMiddleware
- ✅ Sesión 17: Auth JWT — Login, Register, JWTAuth middleware, password hashing (bcrypt)
- ✅ Sesión 18: CORS, Seguridad y Variables de Entorno — CORS, security headers, JWT secret desde env, AUTH_PROVIDER
- ✅ **Sesión 19: Testing y Refinamiento** — Tests de auth (12) y middleware (5), 227 tests total
- Suite: **227 tests passing, 0 skipped, 0 warnings**

## Contexto relevante

- `get_sqlite_connection()` abre/cierra conexión por operación — overhead evitable
- `UsuarioRepositorySQLite` en `retrieve_user_handler` crea repo nuevo por request
- OutboxWorker ya tiene polling configurable; posibles cuellos de botella en DB compartida
- Sin caché de consultas (p.ej. `list_proyectos` siempre a DB)

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
.venv\Scripts\pytest -v
python -m uvicorn src.entrypoint.app:create_app --factory --host 127.0.0.1 --port 8000
```
