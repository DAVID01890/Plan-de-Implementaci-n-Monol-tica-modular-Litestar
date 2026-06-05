# ▶️ Próxima Sesión — Handoff

## Sesión 15: Configuración de Plugins y Variables de Entorno

**Objetivo:** Configuración centralizada con `Litestar` plugins, gestión de entorno, y limpieza de los deprecation warnings de Litestar en path parameters (`proyecto_id`, `sprint_id`).

**Criterio de éxito:** App arranca sin deprecation warnings; configuración manejada desde un solo punto.

## Estado actual del proyecto

- ✅ Sesión 1–9: Estructura, Shared Kernel, IdP, Scrum domain
- ✅ Sesión 10: `Proyecto` aggregate, `Sprint`, exclusividad temporal
- ✅ Sesión 11: `connection.py`, `schema.py`, Alembic migraciones
- ✅ Sesión 12: Repositorios SQLite + Turso, API REST (9 endpoints), DI Litestar
- ✅ Sesión 13: Transactional Outbox (eventos, tabla, insert atómico, worker background)
- ✅ **Sesión 14: Handlers reales del outbox (LoggingHandler, WebhookHandler, ProjectionHandler)**
- Suite: **212 tests passing, 1 skipped** (respx para webhook test)

## Contexto relevante

- `LoggingHandler` — log estructurado de eventos (siempre activo)
- `WebhookHandler` — POST HTTP a `OUTBOX_WEBHOOK_URL` (opcional)
- `ProjectionHandler` — actualiza `proyecto_read_model` (solo SQLite)
- `OutboxWorker._handle_event` ahora itera sobre `self._handlers`
- Pendiente: migrar path parameters a `FromPath`/`Annotated` para eliminar warnings

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
.venv\Scripts\pytest -v
python -m uvicorn src.entrypoint.app:create_app --factory --host 127.0.0.1 --port 8000
```
