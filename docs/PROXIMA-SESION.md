# ▶️ Próxima Sesión — Handoff

## Sesión 9: Tareas Técnicas y Cohesión

**Objetivo:** Descomponer una Historia en tareas técnicas con su propio estado y estimación.

**Criterio de éxito:** Tests que verifiquen creación de tareas, asignación a una historia, y control de estado individual.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Fase 2 (Shared Kernel): `EntityId`, excepciones, Value Objects genéricos, `DomainEvent`
- ✅ Fase 3 (IdP): `Usuario`, `UserId`, `UserRole`, `IdentityServicePort` + Mock
- ✅ Sesión 8: `StoryPoint`, `HistoriaDeUsuario`, workflow de estados

## Contexto relevante

- El código irá en `src/scrum/domain/`
- Crear `TareaTecnica` como entidad ligada a `HistoriaDeUsuario`
- Crear su Value Object de estimación (horas o puntos pequeños)
- Refinar el modelo de estado para tareas
- Tests en `tests/scrum/`

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
uv run pytest -v
uv run litestar run --reload
```
