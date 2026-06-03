# Sesión 01 — El Cascarón y Dependencias

- **Fecha:** 2026-05-28
- **Fase:** 1 — Preparación y Cimientos Estructurales
- **Estado:** ✅ Completada

---

## Objetivo

Crear el entorno virtual (venv), inicializar Git, crear el archivo `requirements.txt` con Litestar instalado y organizar la estructura de carpetas separando domain, ports, adapters y entrypoint.

## Implementación

### 1. Verificación del entorno
Se confirmaron las herramientas disponibles:
- Python 3.13.7
- uv 0.11.16
- Git 2.54.0

### 2. Creación del entorno virtual
```bash
uv venv .venv --python 3.13
```

### 3. Creación de `requirements.txt`
```txt
litestar>=2.12,<3.0
pytest>=8.0
pytest-asyncio>=0.24
```

Se instalaron las dependencias con:
```bash
uv pip install -r requirements.txt
```
Resultado: 29 paquetes instalados (Litestar 2.22.0, pytest 9.0.3, httpx 0.28.1, etc.)

### 4. Estructura de carpetas (Arquitectura Hexagonal)
```
src/
  shared_kernel/
    domain/         → Tipos base, excepciones, value objects genéricos
    ports/          → Interfaces base
  idp/
    domain/         → Entidades y reglas del Identity Provider (usuarios, roles)
    ports/          → Puerto IdentityServicePort
    adapters/       → Implementaciones (Mock, SQLite, etc.)
  scrum/
    domain/         → Entidades del core de Scrum (HU, tareas, sprints, proyecto)
    ports/          → Puertos del dominio Scrum
    adapters/       → Implementaciones de persistencia y eventos
  entrypoint/       → API Litestar (controladores, middlewares, configuración)
tests/              → Tests unitarios y de integración
```

Se agregaron `__init__.py` en todos los directorios para habilitar imports.

### 5. Inicialización de Git
```bash
git init
git add -A
git commit -m "chore: initial project setup with hexagonal architecture"
```

### 6. `.gitignore`
Se creó ignorando `.venv/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.env`, `*.db`, `*.sqlite`.

## Criterio de Éxito

- ✅ Instalación de dependencias sin errores (29 paquetes instalados)
- ✅ Estructura de directorios correcta con separación hexagonal

## Decisiones Técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Gestor de paquetes | `uv` | Más rápido que pip, el usuario ya lo tiene instalado |
| Framework ASGI | Litestar 2.22 | Última versión estable, soporte nativo de DI y DTOs |
| Python | 3.13.7 | Versión disponible en el sistema |
| Estructura | Hexagonal (domain/ports/adapters/entrypoint) | Separación clara de capas, testabilidad, alineado con DDD |

## Archivos creados/modificados

| Archivo | Acción |
|---------|--------|
| `.venv/` | Creado |
| `requirements.txt` | Creado |
| `.gitignore` | Creado |
| `src/**/__init__.py` | Creado (15 archivos) |

## Conclusión

**¿Qué?** Se creó la estructura completa del proyecto: entorno virtual, dependencias, arquitectura hexagonal de carpetas (domain/ports/adapters/entrypoint) e inicialización de Git.

**¿Por qué?** Para establecer una base sólida que separe responsabilidades por capa. La arquitectura hexagonal aísla el dominio de la infraestructura, permitiendo testear reglas de negocio sin depender de bases de datos, APIs o frameworks.

**¿Cómo?** Usando `uv` para el entorno virtual, instalando Litestar como framework ASGI, y organizando 4 módulos raíz (`shared_kernel`, `idp`, `scrum`, `entrypoint`) cada uno con su estructura hexagonal interna. Se agregaron `__init__.py` en todos los directorios para habilitar imports.

## Estado del proyecto al cierre

- Working tree limpio (`git status` limpio)
- Último commit: `6c6b7c7` — `chore: initial project setup with hexagonal architecture`
- Dependencias instaladas y funcionales
- Listo para comenzar Sesión 2 (Health Check con Litestar)
