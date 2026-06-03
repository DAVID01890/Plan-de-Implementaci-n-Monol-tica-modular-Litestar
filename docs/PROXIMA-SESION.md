# ▶️ Próxima Sesión — Handoff

## Sesión 8: Historias de Usuario y Estimación Fibonacci

**Objetivo:** Crear las primeras entidades del dominio Scrum: `HistoriaDeUsuario` con estimación Fibonacci y su Value Object `StoryPoint`.

**Criterio de éxito:** Tests que verifiquen creación de historias, asignación de puntos Fibonacci y validación de valores permitidos.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Fase 2 (Shared Kernel): `EntityId`, excepciones, Value Objects genéricos, `DomainEvent`
- ✅ Fase 3 (IdP): `Usuario`, `UserId`, `UserRole`, `IdentityServicePort` + Mock

## Contexto relevante

- El código irá en `src/scrum/domain/`
- Crear `value_objects.py` con `StoryPoint` (1, 2, 3, 5, 8, 13, 21)
- Crear `entities.py` con `HistoriaDeUsuario` (título, descripción, puntos, estado)
- Tests en `tests/scrum/`

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
uv run pytest -v
uv run litestar run --reload
```
