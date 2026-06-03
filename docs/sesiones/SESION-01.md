# Sesión 01 — El Cascarón y Dependencias

- **Fecha:** 2026-05-28
- **Fase:** 1 — Preparación y Cimientos Estructurales
- **Estado:** ✅ Completada

---

## Objetivo

Crear el entorno virtual con `uv`, instalar Litestar, inicializar Git y organizar la estructura hexagonal de carpetas (domain/ports/adapters/entrypoint).

---

## Implementación

### Entorno y dependencias

- `uv venv .venv --python 3.13` — Entorno virtual con Python 3.13.7
- `requirements.txt`: `litestar>=2.12,<3.0`, `pytest>=8.0`, `pytest-asyncio>=0.24`
- `uv pip install -r requirements.txt` → 29 paquetes instalados (Litestar 2.22.0)

### Estructura hexagonal

```
src/
  shared_kernel/   → Tipos base, value objects, interfaces (Domain/Ports)
  idp/             → Identity Provider (Usuario, roles)
  scrum/           → Core de Scrum (HU, tareas, sprints)
  entrypoint/      → API Litestar (controladores, middlewares)
tests/
```

Se agregaron `__init__.py` en los 15 directorios para habilitar imports.

### Git

- `git init` → commit inicial: `6c6b7c7`
- `.gitignore`: `.venv/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.env`, `*.db`

---

## Archivos creados

| Archivo | Acción |
|---------|--------|
| `.venv/` | Creado |
| `requirements.txt` | Creado |
| `.gitignore` | Creado |
| `src/**/__init__.py` | Creado (15 archivos) |

---

## Conclusión

Esta sesión sentó las bases físicas del proyecto. La arquitectura hexagonal no es solo una estructura de carpetas: es una decisión de diseño que aísla el dominio del mundo exterior. Al separar `domain/` (reglas de negocio), `ports/` (contratos), `adapters/` (implementaciones técnicas) y `entrypoint/` (punto de entrada), garantizamos que las reglas de negocio se puedan testear sin depender de bases de datos, HTTP o frameworks. Litestar 2.22 como framework ASGI aporta tipado fuerte, DI nativa y DTOs sin necesidad de capas adicionales. Todo lo que sigue se construye sobre este esqueleto.

---

## Próxima sesión

**Sesión 2: Health Check con Litestar** — `GET /health` y su test.
