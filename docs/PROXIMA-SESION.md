# ▶️ Próxima Sesión — Handoff

## Sesión 18: CORS, Seguridad y Variables de Entorno

**Objetivo:** Agregar CORS middleware, security headers (helmet-like), mover JWT secret a variable de entorno, y conectar `AUTH_PROVIDER` al Settings.

**Criterio de éxito:** Frontend puede consumir la API desde otro origen; headers de seguridad activos; JWT secret configurable desde `.env`.

## Estado actual del proyecto

- ✅ Sesión 1–9: Estructura, Shared Kernel, IdP, Scrum domain
- ✅ Sesión 10: `Proyecto` aggregate, `Sprint`, exclusividad temporal
- ✅ Sesión 11: `connection.py`, `schema.py`, Alembic migraciones
- ✅ Sesión 12: Repositorios SQLite + Turso, API REST (9 endpoints), DI Litestar
- ✅ Sesión 13: Transactional Outbox (eventos, tabla, insert atómico, worker background)
- ✅ Sesión 14: Handlers reales del outbox (LoggingHandler, WebhookHandler, ProjectionHandler)
- ✅ Sesión 15: Configuración centralizada (Settings dataclass, plugins Litestar, eliminar deprecation warnings)
- ✅ Sesión 16: Controladores HTTP (ProyectoController) + RequestLoggingMiddleware
- ✅ **Sesión 17: Auth JWT** — Login, Register, JWTAuth middleware, password hashing (bcrypt)
- Suite: **212 tests passing, 0 skipped, 0 warnings**

## Contexto relevante

- `src/entrypoint/auth/` contiene todo el módulo de autenticación
- `JWTAuth` protege todas las rutas excepto `/health`, `/auth/login`, `/auth/register`, `/schema`
- JWT secret hardcodeado en `auth/config.py` → mover a `.env`
- No hay CORS configurado → bloquea requests desde frontend en otro origen
- No hay security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- `Settings` tiene `is_turso_enabled` pero no `AUTH_PROVIDER`

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
.venv\Scripts\pytest -v
python -m uvicorn src.entrypoint.app:create_app --factory --host 127.0.0.1 --port 8000
```
