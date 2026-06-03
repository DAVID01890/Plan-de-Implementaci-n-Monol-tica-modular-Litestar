# ▶️ Próxima Sesión — Handoff

## Sesión 7: El Puerto IdentityServicePort (Interfaz y Mock)

**Objetivo:** Definir el puerto (interfaz) `IdentityServicePort` y su implementación Mock para el módulo IdP.

**Criterio de éxito:** Tests que verifiquen el contrato del puerto usando el Mock.

## Estado actual del proyecto

- ✅ Sesión 1: Estructura hexagonal y dependencias
- ✅ Sesión 2: Health Check con Litestar (`GET /health`)
- ✅ Sesión 3: `EntityId` (UUID v4) y excepciones base del dominio
- ✅ Sesión 4: `Email`, `NotEmptyString`, `PositiveInt` (Value Objects genéricos)
- ✅ Sesión 5: `DomainEvent` (base para eventos de dominio)
- ✅ Sesión 6: `Usuario` con `UserId`, `UserRole` y reglas de negocio (activar, desactivar, cambiar rol)

## Contexto relevante

- El puerto irá en `src/idp/ports/`
- El mock irá en `src/idp/adapters/mock/`
- El puerto define el contrato para operaciones sobre usuarios (crear, buscar por ID, buscar por email, listar, actualizar rol)
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
