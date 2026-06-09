# ▶️ Próxima Sesión — Handoff

## Sesión 19: Testing y Refinamiento

**Objetivo:** Agregar tests para auth (login/register, token inválido, expirado), mejorar cobertura de middleware, y refinar manejo de errores.

**Criterio de éxito:** Tests cubren flujos de auth (registro, login, token inválido, sin token); cobertura >90% en módulos entrypoint.

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
- ✅ **Sesión 18: CORS, Seguridad y Variables de Entorno** — CORS, security headers, JWT secret desde env, AUTH_PROVIDER
- Suite: **212 tests passing, 0 skipped, 0 warnings**

## Contexto relevante

- CORS abierto (`allow_origins=["*"]`) — restringir antes de producción
- Security headers activos: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy
- `.env` acepta `JWT_SECRET`, `JWT_ALGORITHM`, `AUTH_PROVIDER`
- `AUTH_PROVIDER` declarado en Settings pero sin efecto todavía
- Faltan tests específicos para auth (login fallido, token expirado, rutas sin auth)

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
.venv\Scripts\pytest -v
python -m uvicorn src.entrypoint.app:create_app --factory --host 127.0.0.1 --port 8000
```
