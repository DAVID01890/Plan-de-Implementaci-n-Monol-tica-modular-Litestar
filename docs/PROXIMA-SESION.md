# ▶️ Próxima Sesión — Handoff

## Sesión 3: Identificadores Únicos y Excepciones

**Objetivo:** Crear las bases del Shared Kernel: objetos de valor genéricos (`EntityId`, `DomainError`) y manejo de excepciones del dominio.

**Criterio de éxito:** Tests que verifiquen la creación de IDs únicos (UUID) y excepciones base del dominio.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ⏳ **Shared Kernel vacío — sin clases ni tipos aún**

## Contexto relevante

- Todo irá en `src/shared_kernel/domain/`
- Crear `base_value_objects.py` con `EntityId` (UUID v4)
- Crear `base_exceptions.py` con `DomainError` y subtipos
- Tests en `tests/shared_kernel/`

## Comandos útiles

```powershell
uv run pytest -v
uv run litestar run --reload
```
