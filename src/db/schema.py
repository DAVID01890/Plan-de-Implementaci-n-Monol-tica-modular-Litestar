CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS proyectos (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sprints (
    id TEXT PRIMARY KEY,
    proyecto_id TEXT NOT NULL REFERENCES proyectos(id),
    nombre TEXT NOT NULL,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    status TEXT NOT NULL DEFAULT 'planned'
);

CREATE TABLE IF NOT EXISTS historias (
    id TEXT PRIMARY KEY,
    proyecto_id TEXT NOT NULL REFERENCES proyectos(id),
    sprint_id TEXT REFERENCES sprints(id),
    titulo TEXT NOT NULL,
    descripcion TEXT,
    story_points INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS tareas_tecnicas (
    id TEXT PRIMARY KEY,
    historia_id TEXT NOT NULL REFERENCES historias(id),
    titulo TEXT NOT NULL,
    descripcion TEXT,
    estimated_hours INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'developer',
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS outbox_events (
    id TEXT PRIMARY KEY,
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    processed_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proyecto_read_model (
    proyecto_id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    total_historias INTEGER NOT NULL DEFAULT 0,
    total_story_points INTEGER NOT NULL DEFAULT 0,
    sprint_actual_id TEXT,
    sprint_actual_nombre TEXT,
    updated_at TEXT NOT NULL
);
"""
