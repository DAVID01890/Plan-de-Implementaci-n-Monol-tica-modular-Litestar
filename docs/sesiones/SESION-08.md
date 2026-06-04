# Sesión 08 — Historias de Usuario y Estimación Fibonacci

- **Fecha:** 2026-06-04
- **Fase:** 4 — Core de Scrum (Dominio Complejo)
- **Estado:** ✅ Completada

---

## Objetivo

Crear las primeras entidades del dominio Scrum: `HistoriaDeUsuario` (una tarea o feature del producto) y su sistema de estimación con `StoryPoint` usando la secuencia Fibonacci.

**Criterio de éxito:** Tests que verifiquen creación de historias, asignación de puntos Fibonacci y validación de valores permitidos.

---

## Implementación

### `src/scrum/domain/value_objects.py` — StoryPoint

```python
_VALID_FIBONACCI_VALUES = frozenset({1, 2, 3, 5, 8, 13, 21})

class StoryPoint:
    _value: int

    def __init__(self, value: int) -> None:
        if value not in _VALID_FIBONACCI_VALUES:
            valid = sorted(_VALID_FIBONACCI_VALUES)
            raise ValidationError(
                f"StoryPoint must be one of {valid}, got {value}"
            )
        self._value = value
```

**¿Qué es un Value Object?** Un Value Object es un objeto que se identifica por **lo que es, no por quién es**. Dos StoryPoint con valor 5 son intercambiables. A diferencia de una entidad (como `Usuario`), no tiene identidad propia — no necesita un ID. Se usa para representar conceptos del dominio que son inmutables y se comparan por valor.

**¿Por qué Fibonacci?** En Scrum, los Story Points miden el **esfuerzo relativo** de una tarea, no horas exactas. La secuencia Fibonacci (1, 2, 3, 5, 8, 13, 21) obliga a que la diferencia entre valores pequeños sea precisa (1→2) pero entre valores grandes sea más difusa (13→21). Esto refleja que es más fácil estimar tareas pequeñas que grandes. Usar `frozenset` para los valores válidos garantiza que la lista no se pueda modificar accidentalmente.

### `src/scrum/domain/entities.py` — HistoriaDeUsuario

```python
class HistoriaId(EntityId):
    pass

class HistoriaStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class HistoriaDeUsuario:
    _id: HistoriaId
    _title: NotEmptyString
    _description: str | None
    _story_points: StoryPoint
    _status: HistoriaStatus
```

**¿Qué es una Entidad?** Una Entidad tiene un ciclo de vida y se identifica por su ID, no por sus atributos. Dos `HistoriaDeUsuario` pueden tener el mismo título y puntos, pero si tienen distinto `HistoriaId`, son diferentes. Esto permite que la entidad cambie sus atributos con el tiempo (ej: cambiar de estado) manteniendo su identidad.

**Máquina de estados del workflow:**

```
PENDING  →  IN_PROGRESS  →  DONE
   ↑                           |
   └───────────────────────────┘  (reopen)
```

Los métodos `start_work()`, `complete()` y `reopen()` controlan estas transiciones. Si intentas un movimiento inválido (ej: completar una historia que nunca se empezó), lanzan `BusinessRuleError`. Esto se llama **comportamiento rico**: la entidad no es solo datos, tiene reglas de negocio encapsuladas.

**`HistoriaId`** hereda de `EntityId` (creado en Sesión 3). Es una herencia vacía porque el comportamiento ya está en la clase padre. En Domain-Driven Design, tener clases separadas aunque estén vacías ayuda a que el código sea más expresivo — sabes exactamente qué tipo de ID espera cada entidad.

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/scrum/test_story_point.py` | 9 | Creación con valores válidos (7 Fibonacci), inválidos (4, 0, -1, 100), igualdad, hash, str |
| `tests/scrum/test_historia_de_usuario.py` | 18 | Creación (4), workflow (3), errores de estado (5), igualdad (3), str/repr (3) |

```
100 passed in 0.98s  (incluye regresión de Sesiones 1-7)
```

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/scrum/domain/value_objects.py` | `StoryPoint` con validación Fibonacci |
| `src/scrum/domain/entities.py` | `HistoriaDeUsuario` con `HistoriaId`, `HistoriaStatus` y workflow |
| `tests/scrum/__init__.py` | Paquete de tests del módulo Scrum |
| `tests/scrum/test_story_point.py` | 9 tests para StoryPoint |
| `tests/scrum/test_historia_de_usuario.py` | 18 tests para HistoriaDeUsuario |

---

## Conclusión

Esta sesión da el primer paso en el **Core de Scrum**, el módulo más complejo y con más lógica de negocio del proyecto. Creamos dos piezas fundamentales:

- **StoryPoint**: un Value Object que encapsula la regla "los puntos de historia solo pueden ser Fibonacci". Al ser inmutable y autovalidarse, eliminamos la posibilidad de tener historias con puntos inválidos en todo el código.
- **HistoriaDeUsuario**: una Entidad con estado que modela el ciclo de vida de una tarea en Scrum. Sus métodos `start_work`, `complete`, `reopen` reflejan el lenguaje del negocio (Ubiquitous Language de DDD).

La estructura sigue el mismo patrón que el módulo IdP (sesiones 6-7): Value Objects simples, Entidades con comportamiento, y tests que cubren tanto el caso feliz como los errores. Esto prepara el terreno para la Sesión 9 (Tareas Técnicas) y Sesión 10 (el Agregado Proyecto con Sprints).

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Validación Fibonacci | `frozenset` + constructor | Inmutable, sin dependencias, error temprano |
| Estado del workflow | `Enum` con 3 valores | Sencillo, sin bibliotecas externas, suficiente para el modelo actual |
| Herencia de `HistoriaId` | Clase vacía que extiende `EntityId` | Reutiliza UUID ya implementado, pero da nombre semántico al tipo |
| `description` como `str \| None` | No usa `NotEmptyString` | La descripción es opcional y puede tener cualquier texto |

---

## Próxima sesión

**Sesión 9: Tareas Técnicas y Cohesión** — Descomponer una Historia en tareas técnicas con su propio estado y estimación.
