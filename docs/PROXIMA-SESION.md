# ▶️ Próxima Sesión — Handoff

## Sesión 5: Contratos de Eventos

**Objetivo:** Definir las interfaces base para eventos de dominio (Domain Events) en el Shared Kernel.

**Criterio de éxito:** Tests que verifiquen la creación, inspección y comparación de eventos de dominio.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Sesión 3: `EntityId` (UUID v4) y excepciones base del dominio
- ✅ Sesión 4: `Email`, `NotEmptyString`, `PositiveInt` (Value Objects genéricos)

## Contexto relevante

- Todo irá en `src/shared_kernel/domain/`
- Crear `base_events.py` con `DomainEvent` y clases relacionadas
- Tests en `tests/shared_kernel/`

## Formato de bitácora

Cada sesión debe documentarse siguiendo la plantilla en `docs/sesiones/TEMPLATE.md`:
- **Objetivo** + **Criterio de éxito** al inicio
- **Implementación** con solo el código esencial y conceptos clave (sin explicación línea por línea)
- **Tests** en tabla resumen
- **Conclusión** reflexiva que conecte el qué, por qué y cómo en contexto del proyecto
- **Decisiones técnicas** en tabla

## Comandos útiles

```powershell
uv run pytest -v
uv run litestar run --reload
```
