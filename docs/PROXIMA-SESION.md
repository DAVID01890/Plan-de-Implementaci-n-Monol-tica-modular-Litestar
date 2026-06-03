# ▶️ Próxima Sesión — Handoff

## Sesión 6: Entidad Usuario y Objetos de Valor de Rol

**Objetivo:** Crear la primera entidad del dominio IdP: `Usuario` con sus Value Objects (`UserId`, `UserRole`) y reglas de negocio asociadas.

**Criterio de éxito:** Tests que verifiquen creación de usuarios, asignación de roles y validación de reglas de negocio.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Sesión 3: `EntityId` (UUID v4) y excepciones base del dominio
- ✅ Sesión 4: `Email`, `NotEmptyString`, `PositiveInt` (Value Objects genéricos)
- ✅ Sesión 5: `DomainEvent` (base para eventos de dominio)

## Contexto relevante

- El código irá en `src/idp/domain/`
- Crear `entities.py` con `Usuario` (hereda de `EntityId`)
- Crear `value_objects.py` con `UserRole` (enum: `Admin`, `Developer`, `Viewer`)
- Tests en `tests/idp/`

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
