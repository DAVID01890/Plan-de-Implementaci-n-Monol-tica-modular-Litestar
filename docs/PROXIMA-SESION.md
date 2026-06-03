# ▶️ Próxima Sesión — Handoff

## Sesión 4: Tipos Primitivos (Objetos de Valor Genéricos)

**Objetivo:** Crear objetos de valor genéricos reutilizables en el Shared Kernel: `Email`, `NotEmptyString`, `PositiveInt`.

**Criterio de éxito:** Tests que verifiquen creación válida, validación y rechazo de valores inválidos.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Sesión 3: `EntityId` (UUID v4) y excepciones base del dominio (`DomainError`, `NotFoundError`, `ValidationError`, `BusinessRuleError`)

## Contexto relevante

- Todo irá en `src/shared_kernel/domain/`
- Crear `base_value_objects.py` añadiendo `Email`, `NotEmptyString`, `PositiveInt`
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
