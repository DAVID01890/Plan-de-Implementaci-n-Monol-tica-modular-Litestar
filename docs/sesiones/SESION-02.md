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

---

## Paso a paso detallado

### 1. Revisión del estado del proyecto

Se ejecutaron los siguientes comandos para entender qué existía antes de empezar:

```
git log --oneline -10     # Ver historial: 2 commits (setup inicial + docs)
git status                # Confirmar working tree limpio
```

El proyecto tenía:
- Estructura hexagonal vacía (12 paquetes con `__init__.py` sin contenido)
- `requirements.txt` con `litestar`, `pytest`, `pytest-asyncio`
- `.venv` con dependencias instaladas
- `tests/` vacío
- `docs/` con especificaciones, AVANCE.md, PROXIMA-SESION.md y SESION-01.md

### 2. Lectura del handoff (PROXIMA-SESION.md)

Se leyó `docs/PROXIMA-SESION.md` para conocer las instrucciones exactas de la sesión:
- Crear `src/entrypoint/app.py` con `create_app()` y ruta `GET /health`
- Crear `tests/test_health.py` usando `TestClient`
- No usar `uvicorn` directamente, sino el CLI `litestar run --reload`

### 3. Creación de `src/entrypoint/app.py`

Se escribió el archivo con tres componentes:

```python
from litestar import Litestar, get


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> Litestar:
    return Litestar(route_handlers=[health])
```

**Explicación línea por línea:**

- **`from litestar import Litestar, get`**: Importa la clase principal de la aplicación y el decorador para rutas GET.
- **`@get("/health")`**: Decorador de Litestar que registra la función como manejador de HTTP GET en la ruta `/health`.
- **`async def health() -> dict[str, str]`**: Función asíncrona que retorna un diccionario. Litestar serializa automáticamente a JSON.
- **`return {"status": "ok"}`**: Cuerpo de la respuesta. Litestar lo convierte a `{"status": "ok"}` con HTTP 200 por defecto.
- **`def create_app() -> Litestar`**: Fábrica que construye y retorna la aplicación. Este patrón es esencial para poder testear la app sin efectos secundarios (cada test crea su propia instancia).
- **`return Litestar(route_handlers=[health])`**: Construye la app pasando la lista de handlers. **Nota importante**: el parámetro se llama `route_handlers`, no `routes`. Inicialmente se intentó con `routes=` y falló porque Litestar 2.x usa `route_handlers`.

### 4. Primer intento de test y error

Se creó `tests/test_health.py` y `tests/__init__.py` (necesario para que pytest encuentre los tests), y se ejecutó:

```
uv run pytest -v
```

**Resultado: FAILED**

```
TypeError: Litestar.__init__() got an unexpected keyword argument 'routes'
```

La causa: se usó `Litestar(routes=[health])` pero el constructor espera `route_handlers=`. Se verificó la firma con:

```python
from litestar import Litestar; help(Litestar.__init__)
```

Allí se confirmó que el primer parámetro posicional es `route_handlers`.

### 5. Corrección y test exitoso

Se cambió `routes=` por `route_handlers=` en `app.py` y se re-ejecutó:

```
uv run pytest -v
```

**Resultado: PASSED**

```
tests/test_health.py::test_health_returns_200 PASSED
1 passed in 0.74s
```

### 6. Explicación del test

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

- **`TestClient(app)`**: Cliente HTTP de prueba incluido en Litestar (basado en httpx). Levanta la app en modo test sin necesidad de un servidor real.
- **`client.get("/health")`**: Hace una petición GET a la ruta.
- **`assert response.status_code == 200`**: Verifica que el servidor responde HTTP 200 OK.
- **`assert response.json() == {"status": "ok"}`**: Verifica que el cuerpo JSON es exactamente el esperado.

### 7. Documentación de la sesión

Se crearon/actualizaron los siguientes archivos:

- **`docs/sesiones/SESION-02.md`**: Bitácora detallada de la sesión (este archivo).
- **`docs/AVANCE.md`**: Se marcó la Sesión 2 como ✅ Completada y se actualizó la fecha.
- **`docs/PROXIMA-SESION.md`**: Se reescribió para apuntar a la Sesión 3 (Shared Kernel).

### 8. Commit

```
git add -A
git commit -m "feat: add health check endpoint (Session 2)"
```

Commit `bf3aa1e` con 7 archivos: 3 nuevos (`app.py`, `test_health.py`, `SESION-02.md`) y 4 modificados.

---

## Comandos ejecutados

```powershell
# Ver historial
git log --oneline -10

# Ver estado
git status

# Ejecutar tests
uv run pytest -v

# Verificar firma del constructor (solo para debugging)
.venv\Scripts\activate; python -c "from litestar import Litestar; help(Litestar.__init__)"

# Commit final
git add -A
git commit -m "feat: add health check endpoint (Session 2)"
```

## Salida de tests

```
tests/test_health.py::test_health_returns_200 PASSED
1 passed in 0.74s
```

## Próxima sesión

**Sesión 3: Identificadores Únicos y Excepciones** — Shared Kernel: base value objects como `EntityId` y excepciones base del dominio. Todo irá en `src/shared_kernel/domain/` con sus tests en `tests/shared_kernel/`.
