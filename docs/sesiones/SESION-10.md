# Sesión 10 — El Agregado Proyecto y el Sprint (Exclusividad Temporal)

- **Fecha:** 2026-06-04
- **Fase:** 4 — Core de Scrum (Dominio Complejo)
- **Estado:** ✅ Completada

---

## Objetivo

Crear `Proyecto` como raíz del agregado que contendrá Sprints, Historias y Tareas, e implementar la regla de exclusividad temporal: una historia no puede estar en dos sprints activos simultáneamente.

**Criterio de éxito:** Tests que verifiquen creación de proyectos, sprints, asignación de historias a sprints, y la regla de exclusividad temporal.

---

## Implementación

### `src/scrum/domain/entities.py` — Agregado Proyecto

El agregado `Proyecto` es la raíz que contiene y coordina sprints e historias:

```python
class Proyecto:
    _id: ProyectoId
    _nombre: NotEmptyString
    _sprints: dict[SprintId, Sprint]
    _historias: dict[HistoriaId, HistoriaDeUsuario]
```

**¿Por qué `Proyecto` es el agregado raíz?** En DDD, el agregado es la unidad de consistencia. `Proyecto` es el contenedor natural: las historias no existen sin un proyecto, los sprints no existen sin un proyecto. Todos los cambios en historias o sprints pasan por `Proyecto`, garantizando que las invariantes (como la exclusividad temporal) se mantengan.

### `src/scrum/domain/entities.py` — Sprint

```python
class SprintStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    CLOSED = "closed"

class Sprint:
    _status: SprintStatus
    _backlog: list[HistoriaId]
```

**Workflow:** `PLANNED → ACTIVE → CLOSED`. Un sprint en `PLANNED` se puede modificar (agregar/quitar historias). Al iniciarlo pasa a `ACTIVE` y se registra `fecha_inicio`. Al cerrarlo pasa a `CLOSED` con `fecha_fin`.

### Exclusividad Temporal

La regla: una historia asignada a un sprint activo no puede asignarse a otro sprint activo. Se implementa en `Proyecto.add_historia_to_sprint()`:

```python
for existing_sprint in self._sprints.values():
    if (
        existing_sprint.status is SprintStatus.ACTIVE
        and historia_id in existing_sprint.backlog
    ):
        raise BusinessRuleError(...)
```

Esta validación se ejecuta **antes** de agregar la historia al sprint destino. Si la historia ya está en otro sprint activo, la operación se rechaza. Esto evita que un desarrollador reciba trabajo duplicado en dos sprints simultáneos, que es la razón de negocio detrás de la regla.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/scrum/test_sprint.py` | 34 | Creación Sprint/Proyecto, workflow (start/close), backlog, exclusividad temporal, igualdad, str/repr |

```
162 passed in 1.20s
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/scrum/domain/value_objects.py` | `StoryPoint`, `HorasEstimadas` — Value Objects con autovalidación |
| `src/scrum/domain/entities.py` | `Proyecto`, `ProyectoId`, `Sprint`, `SprintId`, `SprintStatus`, `HistoriaId`, `HistoriaStatus`, `HistoriaDeUsuario`, `TareaTecnicaId`, `TareaTecnicaStatus`, `TareaTecnica` |
| `src/shared_kernel/domain/` | `EntityId`, `DomainEvent`, excepciones base, Value Objects genéricos |
| `tests/scrum/test_sprint.py` | 34 tests |
| `tests/scrum/test_story_point.py` | 9 tests |
| `tests/scrum/test_historia_de_usuario.py` | 15 tests |
| `tests/scrum/test_horas_estimadas.py` | 9 tests |
| `tests/scrum/test_tarea_tecnica.py` | 15 tests |

---

## Conclusión

Esta sesión consolida el Core de Scrum introduciendo el concepto de **Agregado** como unidad de consistencia transaccional. `Proyecto` es la raíz que garantiza que las invariantes del negocio —como la exclusividad temporal de historias en sprints activos— se cumplan siempre, sin importar desde dónde se intente modificar el estado.

La relación entre `Proyecto`, `Sprint`, `HistoriaDeUsuario` y `TareaTecnica` forma una jerarquía clara: proyecto → sprints → historias → tareas. Cada nivel hereda el contexto del nivel superior, pero solo el agregado raíz (`Proyecto`) controla el acceso a todos sus componentes.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Agregado raíz | `Proyecto` (no `Sprint`) | Contenedor natural, todas las invariantes se verifican desde un solo punto |
| Exclusividad temporal | Validación en `add_historia_to_sprint` | BusinessRuleError con código 409, clara para la API |
| Referencias por ID | `HistoriaId` en backlog del Sprint | Bajo acoplamiento entre entidades |
| Fibonaccis fijos | `frozenset({1,2,3,5,8,13,21})` | Elimina validación externa, error en creación |

---

## Próxima sesión

**Sesión 11: Base de Datos Local y Migraciones** — Configurar SQLite + Alembic para persistir entidades.
