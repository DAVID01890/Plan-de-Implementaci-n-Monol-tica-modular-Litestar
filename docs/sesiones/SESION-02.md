# 📝 Sesión 2: Hola Mundo ASGI (Health Check)

**Fecha:** 2026-06-02

**Duración:** ~15 min

---

## Objetivo

Crear la aplicación Litestar más simple posible exponiendo la ruta `/health` y su test correspondiente.

## Resultado

- ✅ `src/entrypoint/app.py` — fábrica `create_app()` con ruta `GET /health`
- ✅ `tests/test_health.py` — test con `TestClient` verificando HTTP 200 y JSON `{"status": "ok"}`
- ✅ `tests/__init__.py` — para que pytest descubra los tests

## Detalles técnicos

- Se usó `@get("/health")` de Litestar para definir el handler
- El constructor de `Litestar` recibe los handlers vía `route_handlers=`, no `routes=`
- `create_app()` permite testear la app sin efectos secundarios

## Comandos ejecutados

```powershell
uv run pytest -v
```

## Salida de tests

```
tests/test_health.py::test_health_returns_200 PASSED
1 passed in 0.74s
```

## Próxima sesión

**Sesión 3: Identificadores Únicos y Excepciones** — Shared Kernel: base value objects como `EntityId` y excepciones base del dominio.
