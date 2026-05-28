# ▶️ Próxima Sesión — Handoff

## Sesión 2: Hola Mundo ASGI (El Health Check)

**Objetivo:** Crear el archivo `main.py` más simple posible para levantar Litestar y exponer la ruta `/health`.

**Criterio de éxito:** Escribir un test con `TestClient` que verifique que el servidor responde HTTP 200 OK.

## Estado actual del proyecto

- ✅ Entorno virtual creado y activable (`.venv/`)
- ✅ Dependencias instaladas (Litestar 2.22.0, pytest 9.0.3)
- ✅ Estructura hexagonal montada (`src/` con domain/ports/adapters/entrypoint)
- ✅ Git inicializado con commit inicial
- ⏳ **No hay ningún archivo `main.py` ni ruta `/health` aún**

## Contexto relevante

- El entrypoint de la aplicación irá en `src/entrypoint/`
- Usaremos `TestClient` de Litestar (que viene incluido, basado en httpx)
- La sesión debe crear:
  1. Una aplicación Litestar mínima en `src/entrypoint/app.py` (o `main.py`)
  2. Un test en `tests/test_health.py` usando `TestClient`

## Comandos útiles para retomar

```powershell
# Activar entorno
.venv\Scripts\activate

# Ejecutar tests
uv run pytest -v

# Ejecutar app en modo dev
uv run litestar run --reload
```

## Notas

- No usar `uvicorn` directamente; Litestar tiene su propio CLI (`litestar run`)
- La estructura de la app debe ser modular desde el inicio: `src/entrypoint/app.py` con `create_app()` para poder testearla
