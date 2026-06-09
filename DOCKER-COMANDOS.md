# Docker — Paso a Paso

## Requisitos

- Docker Desktop instalado y corriendo
- PowerShell abierto

## 1. Ubicación

Todos los comandos se ejecutan desde la raíz del proyecto:

```powershell
cd C:\Users\vlope\Desktop\PoC
```

Verifica que estás en el lugar correcto:

```powershell
ls Dockerfile
```

Debe mostrar `Dockerfile` (el archivo existe).

---

## 2. Build de la imagen

```powershell
docker build -t plan-implementacion .
```

**Explicación:**
- `-t plan-implementacion` — nombre de la imagen
- `.` — contexto de build (el directorio actual, raíz del proyecto)

El Dockerfile usará `.dockerignore` para excluir `.venv/`, `.env`, `__pycache__/`, etc.

Tarda ~1-2 minutos la primera vez (descarga `python:3.13-slim` e instala dependencias).

---

## 3. Run del contenedor

### Opción A — Usando el archivo `.env`

```powershell
docker run -p 8000:8000 --name poc --env-file .env plan-implementacion
```

- `-p 8000:8000` — mapea puerto local → puerto del contenedor
- `--name poc` — nombre del contenedor (para detenerlo después)
- `--env-file .env` — pasa las variables del archivo `.env` al contenedor

### Opción B — Manual (sin .env)

```powershell
docker run -p 8000:8000 --name poc `
  -e TURSO_DATABASE_URL=libsql://planimplementacion-david01890.aws-us-west-2.turso.io `
  -e TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODA2MDE3NDksImlkIjoiMDE5ZTkzYWMtNzkwMS03NWFjLThhYTgtMTMwM2U3NWM1NzRiIiwicmlkIjoiN2FmMDE4MzItMTY3MC00MDhiLTk3ZGUtYmU0MGY0MGJjZmU1In0.l8H7qbvOeQswAgq551OiDFsOI2uTySQWeDZQmlSs9cSM8J6bBn7LSqVTyiL09WTQrxV7zu-au2fQyN0YRBMSBg `
  -e JWT_SECRET=CHANGE-ME-IN-PRODUCTION--32bytes! `
  -e AUTH_PROVIDER=internal `
  plan-implementacion
```

---

## 4. Verificar que funciona

En otra terminal (sin cerrar la del contenedor):

```powershell
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{"status": "ok", "database": "connected"}
```

También puedes probar los demás endpoints:

```powershell
curl http://localhost:8000/debug/profile
```

---

## 5. Detener y limpiar

```powershell
# Detener el contenedor
docker stop poc

# Eliminar el contenedor
docker rm poc

# (Opcional) Eliminar la imagen
docker rmi plan-implementacion
```

---

## 6. MCP Server

El MCP server expone las herramientas del dominio (proyectos, sprints, historias, usuarios) como herramientas que opencode (u otro cliente MCP) puede consumir.

### Opción A — Docker Compose (recomendada)

```powershell
# Build + run API + MCP
docker compose up --build
```

Esto levanta dos contenedores:
- **poc-api** — Litestar en `http://localhost:8000`
- **poc-mcp** — MCP server en `http://localhost:8100` (SSE transport)

### Opción B — Contenedor individual (MCP en SSE)

```powershell
docker build -t plan-implementacion .
docker run -p 8100:8100 --name poc-mcp --env-file .env plan-implementacion python -m src.mcp_server sse
```

### Opción C — Local (stdio)

Para desarrollo local, sin Docker:

```powershell
python -m src.mcp_server stdio
```

Luego configura opencode para conectarse al MCP server en `opencode.json`:

```jsonc
{
  "mcpServers": {
    "poc-planner": {
      // Local (stdio):
      "command": "python",
      "args": ["-m", "src.mcp_server", "stdio"],
      "enabled": true
      //
      // Ó remoto (SSE vía Docker):
      // "url": "http://localhost:8100/sse",
      // "enabled": true
    }
  }
}
```

### Herramientas disponibles

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `health` | — | Verifica DB |
| `register_user` | email, password | Registra usuario |
| `login_user` | email, password | Login, devuelve JWT |
| `create_proyecto` | nombre | Crea proyecto |
| `list_proyectos` | — | Lista proyectos |
| `get_proyecto` | proyecto_id | Proyecto con sprints e historias |
| `add_historia` | proyecto_id, titulo, story_points | Agrega historia |
| `create_sprint` | proyecto_id, nombre | Crea sprint |
| `assign_historia_to_sprint` | proyecto_id, historia_id, sprint_id | Asigna historia a sprint |
| `start_sprint` | proyecto_id, sprint_id | Inicia sprint |

---

## Resumen rápido

| Paso | Comando | Directorio |
|------|---------|------------|
| Build | `docker build -t plan-implementacion .` | `C:\Users\vlope\Desktop\PoC` |
| Run API | `docker run -p 8000:8000 --name poc --env-file .env plan-implementacion` | `C:\Users\vlope\Desktop\PoC` |
| Run API + MCP | `docker compose up --build` | `C:\Users\vlope\Desktop\PoC` |
| Test API | `curl http://localhost:8000/health` | cualquier directorio |
| Test MCP | `curl http://localhost:8100/sse` (SSE endpoint, devuelve event-stream) | cualquier directorio |
| Stop container | `docker stop poc` | cualquier directorio |
