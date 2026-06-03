# Sesión 02 — Hola Mundo ASGI (Health Check)

- **Fecha:** 2026-06-02
- **Fase:** 1 — Preparación y Cimientos Estructurales
- **Estado:** ✅ Completada

---

## Objetivo

Crear la aplicación Litestar más simple posible exponiendo la ruta `/health` y su test correspondiente.

**Criterio de éxito:** Test que verifique HTTP 200 y JSON `{"status": "ok"}` en `GET /health`.

---

## Paso a paso

### 1. Revisión del estado del proyecto

```
git log --oneline -10     # 2 commits: setup inicial + docs
git status                # working tree limpio
```

El proyecto tenía:
- Estructura hexagonal vacía (12 paquetes con `__init__.py` sin contenido)
- `requirements.txt` con `litestar`, `pytest`, `pytest-asyncio`
- `.venv` con dependencias instaladas
- `tests/` vacío (sin `__init__.py`)
- `docs/` con especificaciones, AVANCE.md, PROXIMA-SESION.md y SESION-01.md

### 2. Lectura del handoff (PROXIMA-SESION.md)

Se confirmaron las instrucciones:
- Crear `src/entrypoint/app.py` con `create_app()` y ruta `GET /health`
- Crear `tests/test_health.py` usando `TestClient` de Litestar
- No usar `uvicorn` directamente, sino el CLI `litestar run --reload`

---

## Implementación detallada

### 3. `src/entrypoint/app.py`

```python
from litestar import Litestar, get


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> Litestar:
    return Litestar(route_handlers=[health])
```

**Explicación línea por línea:**

| Línea | Descripción |
|-------|-------------|
| `from litestar import Litestar, get` | Importa la clase principal `Litestar` que representa la aplicación ASGI, y el decorador `get` para registrar rutas HTTP GET. |
| `@get("/health")` | Decorador que registra la función `health` como manejador de la ruta `/health` para el método GET. Internamente, Litestar construye un objeto `Route` con esta función. |
| `async def health() -> dict[str, str]:` | Función asíncrona (corrutina) que maneja la petición. Retorna un diccionario Python que Litestar serializa automáticamente a JSON con `Content-Type: application/json`. |
| `return {"status": "ok"}` | Cuerpo de la respuesta. Litestar asigna HTTP 200 por defecto. El diccionario se convierte en `{"status": "ok"}` en la respuesta HTTP. |
| `def create_app() -> Litestar:` | **Patrón fábrica**: función que construye y retorna la aplicación. Esto permite crear una instancia nueva en cada test sin efectos secundarios entre tests. |
| `return Litestar(route_handlers=[health])` | Construye la app pasando la lista de handlers. **Error común:** el parámetro se llama `route_handlers`, no `routes`. |

**¿Por qué el patrón fábrica `create_app()`?**

En lugar de instanciar `Litestar` directamente en el módulo (lo que ejecutaría código al importar), la fábrica permite:
- Crear una app distinta para cada test (aislamiento)
- Pasar configuraciones diferentes (entorno, plugins, mock de DB) sin modificar el módulo
- Mantener el módulo como un blueprint que no arranca hasta que se llama a `create_app()`

### 4. Primer intento y error

Al ejecutar el test por primera vez:

```
uv run pytest -v
```

**Resultado: FAILED**

```
TypeError: Litestar.__init__() got an unexpected keyword argument 'routes'
```

**Causa:** Se usó `Litestar(routes=[health])` pero el constructor de Litestar 2.x espera `route_handlers=`. Se verificó la firma:

```python
from litestar import Litestar; help(Litestar.__init__)
```

Allí se confirmó que el primer parámetro posicional/palabra clave es `route_handlers`.

**Corrección:** Cambiar `routes=` por `route_handlers=` en `app.py`.

### 5. `tests/test_health.py`

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

**Explicación línea por línea:**

| Línea | Descripción |
|-------|-------------|
| `from litestar.testing import TestClient` | Importa el cliente HTTP de prueba incluido en Litestar. Está basado en `httpx` y permite hacer peticiones a la app sin levantar un servidor real. |
| `from src.entrypoint.app import create_app` | Importa la fábrica para crear una instancia de la app. |
| `def test_health_returns_200() -> None:` | Test unitario. El nombre descriptivo permite identificar qué falla sin leer el código. |
| `app = create_app()` | Crea una instancia limpia de la aplicación Litestar. Cada test crea su propia app, evitando efectos laterales. |
| `with TestClient(app) as client:` | Context manager que envuelve la app en un cliente HTTP de prueba. El `with` garantiza limpieza de recursos. |
| `response = client.get("/health")` | Hace una petición GET a la ruta `/health`. El cliente internamente construye un ASGI scope, llama a la app directamente (sin socket TCP), y devuelve un objeto `Response`. |
| `assert response.status_code == 200` | Verifica que el servidor responde con HTTP 200 OK. Código estándar para respuestas exitosas. |
| `assert response.json() == {"status": "ok"}` | Verifica que el cuerpo JSON coincide exactamente con lo esperado. `response.json()` parsea el body y lo convierte a dict de Python. |

**¿Por qué `TestClient` y no hacer peticiones reales?**

| Opción | Ventaja | Desventaja |
|--------|---------|------------|
| `TestClient` | No necesita puerto TCP, es instantáneo, no hay colisiones de puertos | No prueba el network stack real |
| Servidor real (httpx) | Prueba el servidor real | Más lento, requiere gestión de puertos, tests dependientes del entorno |

Para un PoC, `TestClient` es más rápido y suficiente. En tests de integración se usaría un servidor real.

### 6. Test exitoso

```
uv run pytest -v
```

```
tests/test_health.py::test_health_returns_200 PASSED
1 passed in 0.74s
```

---

## Archivos creados/modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/entrypoint/app.py` | ✅ Creado | Fábrica `create_app()` y ruta `GET /health` |
| `tests/__init__.py` | ✅ Creado | Paquete de tests (vació, necesario para que pytest descubra los tests) |
| `tests/test_health.py` | ✅ Creado | Test con `TestClient` verificando HTTP 200 y JSON |
| `docs/AVANCE.md` | 📝 Modificado | Sesión 2 marcada como ✅, fecha actualizada |
| `docs/PROXIMA-SESION.md` | 📝 Modificado | Handoff actualizado a Sesión 3 |
| `docs/sesiones/SESION-02.md` | ✅ Creado | Bitácora detallada (este archivo) |

---

## Estado del proyecto al cierre

- Working tree limpio (`git status`)
- Último commit: `bf3aa1e` — `feat: add health check endpoint (Session 2)`
- 1 test pasando
- App Litestar funcional con ruta `/health`

---

## Conclusión

**¿Qué?** Se implementó el endpoint `GET /health` con Litestar y su test correspondiente usando `TestClient`.

**¿Por qué?** El health check es el punto de entrada mínimo para verificar que la aplicación ASGI arranca, responde y se puede testear. Sirve como prueba de que la cadena completa (framework → ruta → test) funciona antes de agregar lógica de dominio.

**¿Cómo?** Creando una función `create_app()` que construye la app Litestar (patrón fábrica), registrando un handler con `@get("/health")`, y verificando con `TestClient` que devuelve HTTP 200 y `{"status": "ok"}`.

## Comandos ejecutados

```powershell
# Ver historial y estado
git log --oneline -10
git status

# Ejecutar tests
uv run pytest -v

# Verificar firma del constructor (debugging)
.venv\Scripts\activate; python -c "from litestar import Litestar; help(Litestar.__init__)"

# Commit
git add -A
git commit -m "feat: add health check endpoint (Session 2)"
```

---

## Errores encontrados y solución

| Error | Causa | Solución |
|-------|-------|----------|
| `Litestar.__init__() got an unexpected keyword argument 'routes'` | El parámetro se llama `route_handlers`, no `routes` | Cambiar `routes=` por `route_handlers=` |

---

## Próxima sesión

**Sesión 3: Identificadores Únicos y Excepciones** — Shared Kernel: `EntityId` (UUID v4) y excepciones base del dominio (`DomainError`, `NotFoundError`, `ValidationError`, `BusinessRuleError`).
