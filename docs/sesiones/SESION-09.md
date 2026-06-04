# Sesión 09 — Tareas Técnicas y Cohesión

- **Fecha:** 2026-06-04
- **Fase:** 4 — Core de Scrum (Dominio Complejo)
- **Estado:** ✅ Completada

---

## Objetivo

Crear el concepto de `TareaTecnica`: una sub-tarea que descompone una `HistoriaDeUsuario` en piezas técnicas pequeñas, cada una con su propia estimación en horas y su ciclo de vida.

**Criterio de éxito:** Tests que verifiquen creación de tareas, asignación a una historia, y control de estado individual.

---

## Implementación

### `src/scrum/domain/value_objects.py` — HorasEstimadas

```python
_MAX_HORAS = 40

class HorasEstimadas:
    _value: int

    def __init__(self, value: int) -> None:
        if value <= 0:
            raise ValidationError(f"Horas must be positive, got {value}")
        if value > _MAX_HORAS:
            raise ValidationError(
                f"Horas cannot exceed {_MAX_HORAS}, got {value}"
            )
        self._value = value
```

**¿Por qué otro Value Object?** `HorasEstimadas` encapsula la regla "una tarea técnica no puede estimarse en más de 40 horas (una semana laboral)". Al igual que `StoryPoint`, al ser un Value Object inmutable con autovalidación, eliminamos la posibilidad de tener tareas con horas negativas o irrealmente grandes. La constante `_MAX_HORAS` hace explícito el límite y es fácil de ajustar si cambia la política del equipo.

**¿Por qué `int` y no `float`?** Las estimaciones ágiles suelen darse en horas enteras. Usar `int` evita falsa precisión (nadie estima 3.7 horas) y simplifica la validación.

### `src/scrum/domain/entities.py` — TareaTecnica

```python
class TareaTecnicaId(EntityId):
    pass

class TareaTecnicaStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
```

**Cohesión: ¿qué significa?** Cohesión es el grado en que los elementos de un módulo "pertenecen juntos". `TareaTecnica` vive en el mismo módulo (`scrum.domain`) que `HistoriaDeUsuario` porque ambas pertenecen al mismo concepto de negocio: planificar y ejecutar trabajo en Scrum. Si estuvieran en módulos separados, cada vez que una historia necesitara crear tareas habría que cruzar fronteras de módulo, aumentando la complejidad.

```python
class TareaTecnica:
    _historia_id: HistoriaId

    def __init__(self, historia_id: HistoriaId, ...):
        self._historia_id = historia_id
```

**¿Por qué referencia por ID y no por objeto?** `TareaTecnica` guarda el `HistoriaId` de su historia padre, no una referencia directa al objeto `HistoriaDeUsuario`. Esto es una decisión deliberada de DDD:

- **Bajo acoplamiento**: La tarea no necesita cargar la historia completa para existir. Si solo quieres listar tareas, no arrastras toda la historia.
- **Consistencia**: La identidad de la historia está en su ID. Si la historia cambia de título o puntos, la tarea no se ve afectada.
- **Preparación para persistencia**: En la base de datos, la relación será una foreign key `historia_id`. Modelarlo así desde el dominio hace que el salto a SQL sea trivial.

**Workflow simplificado:**

```
PENDING  →  IN_PROGRESS  →  DONE
```

A diferencia de `HistoriaDeUsuario`, `TareaTecnica` no tiene `reopen()`. Una tarea completada no se reactiva — si hay más trabajo, se crea otra tarea. Esto refleja que las tareas técnicas son atómicas y de vida corta, mientras que una historia puede volver a abrirse porque representa una funcionalidad completa.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/scrum/test_horas_estimadas.py` | 9 | Creación (4), igualdad (3), str/repr (2) |
| `tests/scrum/test_tarea_tecnica.py` | 15 | Creación (4), workflow (2), errores (3), igualdad (3), str/repr (3) |

```
123 passed in 0.93s  (incluye regresión de Sesiones 1-8)
```

---

## Archivos modificados/creados

| Archivo | Descripción |
|---------|-------------|
| `src/scrum/domain/value_objects.py` | + `HorasEstimadas` (Value Object con tope de 40h) |
| `src/scrum/domain/entities.py` | + `TareaTecnicaId`, `TareaTecnicaStatus`, `TareaTecnica` |
| `tests/scrum/test_horas_estimadas.py` | 9 tests nuevos |
| `tests/scrum/test_tarea_tecnica.py` | 15 tests nuevos |

---

## Conclusión

Esta sesión introduce el segundo nivel de descomposición en el Core de Scrum: las **tareas técnicas**. Mientras que `HistoriaDeUsuario` (Sesión 8) representa una funcionalidad desde la perspectiva del usuario, `TareaTecnica` la descompone en el "cómo" técnico: "implementar formulario de login", "crear tabla en BD", "escribir tests".

La relación entre ambas es la semilla de un **Agregado** (concepto de DDD que veremos en Sesión 10). La historia es la raíz, las tareas son sus hijos. Al referenciar por ID (`historia_id`) en lugar de por objeto, mantenemos bajo acoplamiento y preparamos el terreno para persistencia y para el Agregado `Proyecto` que contendrá Sprints e Historias.

`HorasEstimadas` con su tope de 40h introduce una política de equipo explícita en el código, haciendo que la regla de negocio "una tarea no puede ser de más de una semana" sea imposible de violar.

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Estimación en horas enteras | `int` con tope 40h | Evita falsa precisión, refleja prácticas ágiles reales |
| Relación tarea → historia | `historia_id: HistoriaId` | Bajo acoplamiento, preparado para persistencia |
| Sin `reopen` en tareas | Solo PENDING → IN_PROGRESS → DONE | Tareas son atómicas; trabajo adicional = nueva tarea |
| Ubicación en mismo módulo | `scrum.domain` | Cohesión: ambos conceptos pertenecen al mismo subdominio |

---

## Próxima sesión

**Sesión 10: El Agregado Proyecto y el Sprint (Exclusividad Temporal)** — Crear `Proyecto` como raíz del agregado que contendrá Sprints con sus Historias y Tareas.
