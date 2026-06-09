# Sesión 17 — Auth JWT

- **Fecha:** 2026-06-08
- **Fase:** 7 — Seguridad y Producción
- **Estado:** ✅ Completada

---

## Objetivo

Agregar autenticación JWT al proyecto: gestión de passwords en la entidad `Usuario`, endpoints de registro y login, y middleware que proteja las rutas de la API Scrum.

**Criterio de éxito:** Los endpoints `/proyectos/*` requieren token JWT. Existen `/auth/register` y `/auth/login` públicos. 212 tests pasan.

---

## Implementación

### `src/idp/domain/entities.py` — Password en Usuario

Se agregaron `_password_hash: str | None`, `set_password(password)` que hashea con bcrypt, y `verify_password(password) -> bool` que verifica contra el hash. El hash se persiste como string en la DB.

### `src/entrypoint/auth/` — Módulo de autenticación

| Archivo | Propósito |
|---------|-----------|
| `config.py` | `AuthSettings` con secret, algoritmo y expiración |
| `schemas.py` | `LoginRequest` y `LoginResponse` |
| `guards.py` | `JWTAuth` con `retrieve_user_handler`, exclude paths, guard `require_active_user` |
| `handlers.py` | `POST /auth/login` y `POST /auth/register` |

**`retrieve_user_handler`:** Recibe un `Token` decodificado por Litestar, extrae `token.sub` (UUID del usuario), y busca en `UsuarioRepositorySQLite`.

**JWTAuth config:**
- Excluye `/health`, `/auth/login`, `/auth/register`, `/schema`
- Algoritmo HS256, expiración 1 día
- `on_app_init` registrado en la app

### `src/entrypoint/app.py` — Integración

```python
on_app_init=[_on_app_init, jwt_auth.on_app_init]
route_handlers=[health, login, register, ProyectoController]
```

Se agregó dependencia `usuario_repo` apuntando a `UsuarioRepositorySQLite`.

### `src/db/schema.py` — Nueva columna

```sql
password_hash TEXT
```

### `src/idp/adapters/usuario_repo_sqlite.py`

SELECTs actualizados para incluir `password_hash`. `save` incluye la columna.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/test_proyecto_api.py` | 9 → 9 | Ahora cada test se autentica: register + login + Bearer header en cada request |
| `tests/idp/test_usuario_repo_sqlite.py` | 8 | Ahora lee/escribe `password_hash` correctamente |

```
212 passed in 18.15s
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/entrypoint/auth/__init__.py` | Package init |
| `src/entrypoint/auth/config.py` | AuthSettings dataclass |
| `src/entrypoint/auth/schemas.py` | LoginRequest, LoginResponse |
| `src/entrypoint/auth/guards.py` | JWTAuth instance, retrieve_user_handler, guards |
| `src/entrypoint/auth/handlers.py` | login, register endpoints |

---

## Conclusión

La sesión conecta el módulo IdP (existente desde Sesiones 6-7) con la capa de entrypoint HTTP, cerrando el círculo entre el dominio de identidad y la API. Ahora la API tiene autenticación real: registro de usuarios con contraseña hasheada (bcrypt), login que devuelve JWT firmado, y middleware que protege todos los endpoints de negocio.

La arquitectura se mantiene fiel a DDD: el `Usuario` entity contiene la lógica de password (set/verify), el repositorio abstrae la persistencia, y el módulo `auth/` orquesta la integración con Litestar's `JWTAuth` sin acoplar el dominio al framework.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| bcrypt vs argon2 | bcrypt | Suficiente para PoC, bien soportado, sin dependencias nativas problemáticas en Windows |
| `JWTAuth` de Litestar | Middleware declarativo | Integración nativa con guards, exclude paths, OpenAPI; evita implementar decoding manual |
| `retrieve_user_handler` instancia repo directo | Sin DI | El middleware corre antes de la resolución de dependencias; instanciar `UsuarioRepositorySQLite` es directo y no requiere estado compartido |
| Secret hardcodeado por ahora | `CHANGE-ME-IN-PRODUCTION--32bytes!` | Se moverá a env var en sesión de CORS/seguridad |

---

## Próxima sesión

**Sesión 18: CORS, Seguridad y Variables de Entorno** — CORS middleware para frontend, security headers, mover JWT secret a `.env`, y agregar `AUTH_PROVIDER` al Settings.
