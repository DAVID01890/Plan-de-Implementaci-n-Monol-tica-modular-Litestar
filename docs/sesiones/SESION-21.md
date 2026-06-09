# Sesion 21: Dockerizacion y Despliegue en Render

## Objetivo
Preparar la aplicacion para ser desplegada en Render.com mediante Docker, con zero-downtime y configuracion via variables de entorno.

## Archivos creados

| Archivo | Proposito |
|---------|-----------|
| `Dockerfile` | Multi-stage build (builder + runtime slim) |
| `render.yaml` | Infraestructura como codigo para Render |
| `.dockerignore` | Excluir .venv, .env, __pycache__, docs, tests |

## Cambios realizados

### Health Check mejorado
`src/entrypoint/app.py`:
- `/health` ahora verifica conectividad a la base de datos (Turso o SQLite)
- Retorna `{"status": "ok", "database": "connected"}` en exito
- Retorna `{"status": "degraded", "database": "error"}" en fallo

### Dockerfile
- `python:3.13-slim` como imagen base
- Multi-stage: builder instala dependencias, runtime ejecuta
- Variables de entorno: `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`
- Puerto configurable via `$PORT` (Render asigna dinamicamente)

### render.yaml
- `runtime: image` para usar Dockerfile
- Health check en `/health` (Render monitorea y reinicia si falla)
- Variables sensibles marcadas como `sync: false` (se configuran en dashboard)
- `JWT_SECRET` con autogeneracion (`generateValue: true`)

## Variables de entorno requeridas en Render

| Variable | Origen |
|----------|--------|
| `TURSO_DATABASE_URL` | Dashboard de Turso |
| `TURSO_AUTH_TOKEN` | Dashboard de Turso |
| `JWT_SECRET` | Generada por Render o manual |
| `AUTH_PROVIDER` | `internal` |

## Tests
```powershell
pytest -q  # 254 tests pasando
```

## Comandos utiles

```powershell
# Build local
docker build -t plan-implementacion .

# Run local
docker run -p 8000:8000 ^
  -e TURSO_DATABASE_URL=libsql://... ^
  -e TURSO_AUTH_TOKEN=... ^
  -e JWT_SECRET=... ^
  plan-implementacion
```
