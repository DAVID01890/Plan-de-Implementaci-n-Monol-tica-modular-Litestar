# Sesión 04 — Tipos Primitivos (Objetos de Valor Genéricos)

- **Fecha:** 2026-06-03
- **Fase:** 2 — Shared Kernel (Dominio Base)
- **Estado:** ✅ Completada

---

## Objetivo

Crear objetos de valor genéricos reutilizables en el Shared Kernel: `Email`, `NotEmptyString`, `PositiveInt`.

**Criterio de éxito:** Tests que verifiquen creación válida, validación y rechazo de valores inválidos.

---

## Implementación

### `src/shared_kernel/domain/base_value_objects.py` — Email, NotEmptyString, PositiveInt

```python
_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class Email:
    def __init__(self, value: str) -> None:
        if not _EMAIL_PATTERN.match(value):
            raise ValidationError(f"Invalid email: '{value}'")
        self._value = value


class NotEmptyString:
    def __init__(self, value: str) -> None:
        stripped = value.strip()
        if not stripped:
            raise ValidationError("Value cannot be empty or whitespace")
        self._value = stripped


class PositiveInt:
    def __init__(self, value: int) -> None:
        if value <= 0:
            raise ValidationError(f"Value must be positive, got {value}")
        self._value = value
```

**Conceptos clave:**
- Los tres siguen el mismo patrón que `EntityId`: inmutables, `__eq__`, `__hash__`, `__str__`, `__repr__`
- **Email**: valida formato con regex, lanza `ValidationError` si es inválido
- **NotEmptyString**: rechaza strings vacíos o solo whitespace; **auto-trim** (almacena el valor sin espacios)
- **PositiveInt**: rechaza 0 y negativos
- Todas las validaciones usan `ValidationError` de la jerarquía de dominio (Sesión 3)

---

## Tests

| Archivo | Tests | ¿Qué cubren? |
|---------|-------|--------------|
| `tests/shared_kernel/test_primitive_value_objects.py` | 24 | 9 Email (válidos, inválidos, igualdad, hash), 8 NotEmptyString (trim, vacío, whitespace), 7 PositiveInt (0, negativos, igualdad) |

```
37 passed in 0.72s  (incluye regresión de Sesiones 1-3)
```

---

## Archivos creados/modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/shared_kernel/domain/base_value_objects.py` | 📝 Modificado | Se añadieron `Email`, `NotEmptyString`, `PositiveInt` |
| `tests/shared_kernel/test_primitive_value_objects.py` | ✅ Creado | 24 tests para los 3 nuevos Value Objects |

---

## Conclusión

Estos tres Value Objects cubren necesidades que aparecen constantemente en cualquier dominio: emails que deben ser válidos, textos que no pueden estar vacíos y números que deben ser positivos. Al encapsularlos en el Shared Kernel con su propia validación, cualquier entidad del dominio (IdP o Scrum) puede usarlos sin repetir lógica de validación. El patrón es siempre el mismo: constructor con validación → `ValidationError` si falla → propiedad de solo lectura → dunder methods. Esto crea un lenguaje consistente en todo el proyecto donde "si el objeto existe, el valor es válido".

---

## Decisiones técnicas

| Decisión | Opción | Razón |
|----------|--------|-------|
| Regex de Email | Patrón simple (no RFC 5322) | Suficiente para PoC, evita falsos negativos de regex complejos |
| Auto-trim en NotEmptyString | Sí | Previene errores por espacios accidentales, consistente con formularios web |
| Validación en constructor | Sí (fail-fast) | El objeto nunca existe en estado inválido — invariante de Value Object |

---

## Próxima sesión

**Sesión 5: Contratos de Eventos** — `DomainEvent` base en el Shared Kernel.
