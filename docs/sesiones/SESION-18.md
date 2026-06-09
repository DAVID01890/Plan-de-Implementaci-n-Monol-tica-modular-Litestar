# Sesión 18 — CORS, Seguridad y Variables de Entorno

- **Fecha:** 2026-06-08
- **Fase:** 7 — Seguridad y Producción
- **Estado:** ✅ Completada

---

## Objetivo

Agregar CORS middleware, security headers, mover JWT secret a variable de entorno, y agregar `AUTH_PROVIDER` al Settings.

**Criterio de éxito:** API responde con CORS headers y security headers; JWT secret configurable desde `.env`; 212 tests pasan.

---

## Implementación

### `src/entrypoint/app.py` — CORS config

```python
cors_config = CORSConfig(allow_origins=["*"], allow_credentials=True, max_age=3600)
Litestar(cors_config=cors_config, ...)
```

Permite cualquier origen (PoC), credenciales y cache de preflight por 1 hora.

### `src/entrypoint/middleware.py` — SecurityHeadersMiddleware

Agrega estos headers a toda respuesta HTTP:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### `src/entrypoint/auth/config.py` — AuthSettings.from_env()

```python
@classmethod
def from_env(cls, env_file=None) -> AuthSettings:
    return cls(
        secret=os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION--32bytes!"),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    )
```

### `src/entrypoint/config.py` — Settings con AUTH_PROVIDER y jwt_secret

```python
auth_provider: str = "internal"
jwt_secret: str = "CHANGE-ME-IN-PRODUCTION--32bytes!"
```

---

## Tests

```
212 passed in 17.25s
```

Sin cambios en tests — CORS y security headers son transparentes para el test suite existente.

---

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/entrypoint/app.py` | CORS config + SecurityHeadersMiddleware |
| `src/entrypoint/middleware.py` | Nuevo `SecurityHeadersMiddleware` |
| `src/entrypoint/auth/config.py` | `AuthSettings.from_env()` lee `JWT_SECRET` y `JWT_ALGORITHM` |
| `src/entrypoint/auth/guards.py` | `load_dotenv` + `AuthSettings.from_env()` |
| `src/entrypoint/config.py` | Campos `auth_provider` y `jwt_secret` |

---

## Conclusión

La API ahora es consumible desde un frontend en otro origen (CORS), tiene headers de seguridad básicos que protegen contra攻击 comunes (clickjacking, MIME sniffing, XSS reflejado), y el JWT secret es configurable desde el entorno. El `AUTH_PROVIDER` queda declarado en Settings pero aún sin efecto — prepara el terreno para conectar Supabase Auth en una sesión futura.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| `allow_origins=["*"]` | Abierto | PoC en desarrollo; restringir en producción |
| SecurityHeaders como middleware | ASGI puro | Sin dependencias extra; 4 headers esenciales |
| `AuthSettings.from_env()` | Factory method | Consistente con `Settings.from_env()` |

---

## Próxima sesión

**Sesión 19: Testing y Refinamiento** — Agregar tests para auth (login/register, token inválido, expirado), mejorar cobertura de middleware, y refinar manejo de errores.
