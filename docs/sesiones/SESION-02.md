# Sesión 02 — Hola Mundo ASGI (Health Check)

- **Fecha:** 2026-06-02
- **Fase:** 1 — Preparación y Cimientos Estructurales
- **Estado:** ✅ Completada

---

## Objetivo

Crear la aplicación Litestar más simple con la ruta `GET /health` y su test unitario.

**Criterio de éxito:** Test que verifique HTTP 200 y JSON `{"status": "ok"}`.

---

## Implementación

### `src/entrypoint/app.py`

```python
from litestar import Litestar, get


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> Litestar:
    return Litestar(route_handlers=[health])
```

**Puntos clave:**
- `@get("/health")` registra el handler como ruta GET
- `create_app()` es un **patrón fábrica**: permite crear una app nueva por test, evitando efectos laterales
- El parámetro se llama `route_handlers`, **no** `routes` (error común en Litestar 2.x)

### `tests/test_health.py`

```python
from litestar.testing import TestClient
from src.entrypoint.app import create_app


def test_health_returns_200() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

`TestClient` envuelve la app y permite hacer peticiones HTTP sin levantar un servidor real (basado en `httpx`).

### Error corregido

El primer intento usó `Litestar(routes=[health])` → `TypeError`. Se corrigió a `route_handlers=`.

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/entrypoint/app.py` | Fábrica `create_app()`, ruta `GET /health` |
| `tests/__init__.py` | Paquete de tests |
| `tests/test_health.py` | Test con `TestClient` |

---

## Conclusión

Un health check parece trivial, pero su verdadero valor es probar que toda la cadena ASGI funciona: el framework arranca, las rutas se registran, los decoradores se ejecutan, la serialización JSON ocurre y los tests pueden hacer peticiones reales sin servidor. El patrón fábrica `create_app()` es la puerta de entrada a la testabilidad del proyecto —cada test tendrá su propia instancia de la app sin efectos secundarios—. Resolver el error `routes` vs `route_handlers` en esta etapa (cuando el código es mínimo) evita dolores de cabeza futuros.

---

## Próxima sesión

**Sesión 3: Identificadores Únicos y Excepciones** — Shared Kernel: `EntityId` y excepciones de dominio.
