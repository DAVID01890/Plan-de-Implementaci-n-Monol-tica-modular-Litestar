# ▶️ Próxima Sesión — Handoff

## Sesión 10: El Agregado Proyecto y el Sprint (Exclusividad Temporal)

**Objetivo:** Crear el agregado `Proyecto` que contendrá Sprints con sus Historias de Usuario y Tareas Técnicas. Modelar la exclusividad temporal (una historia no puede estar en dos sprints a la vez).

**Criterio de éxito:** Tests que verifiquen creación de proyecto, inicio/cierre de sprint, asignación de historias a sprints, y validación de que una historia no se asigne a dos sprints activos.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Fase 2 (Shared Kernel): `EntityId`, excepciones, Value Objects genéricos, `DomainEvent`
- ✅ Fase 3 (IdP): `Usuario`, `UserId`, `UserRole`, `IdentityServicePort` + Mock
- ✅ Sesión 8: `StoryPoint`, `HistoriaDeUsuario`, workflow de estados
- ✅ Sesión 9: `HorasEstimadas`, `TareaTecnica`, relación historia-tarea

## Contexto relevante

- El código irá en `src/scrum/domain/`
- Crear `SprintId`, `Sprint` con fechas, backlog y estado
- Crear `Proyecto` como raíz del agregado con colecciones de Sprints e Historias
- Validar que una historia no esté en dos sprints abiertos simultáneamente
- Tests en `tests/scrum/`

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`.

## Comandos útiles

```powershell
uv run pytest -v
uv run litestar run --reload
```
