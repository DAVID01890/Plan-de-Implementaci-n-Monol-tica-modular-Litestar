# Sesión 03 — Identificadores Únicos y Excepciones

- **Fecha:** 2026-06-03
- **Fase:** 2 — Shared Kernel (Dominio Base)
- **Estado:** ✅ Completada

---

## Objetivo

Crear las bases del Shared Kernel: objetos de valor genéricos (`EntityId`) y manejo de excepciones del dominio (`DomainError`, `NotFoundError`, `ValidationError`, `BusinessRuleError`).

## Implementación

### 1. `src/shared_kernel/domain/base_value_objects.py`

Clase `EntityId` basada en UUID v4:
- Si no se pasa valor, genera un UUID v4 automáticamente
- Inmutable (el valor se asigna en `__init__` y se expone como property)
- `__eq__` y `__hash__` para usar como clave en sets/dicts
- `__str__` y `__repr__` para representación legible

### 2. `src/shared_kernel/domain/base_exceptions.py`

Jerarquía de excepciones del dominio:
- `DomainError` — base de todas las excepciones de dominio (hereda de `Exception`)
- `NotFoundError` — entidad no encontrada (formatea mensaje con nombre e ID)
- `ValidationError` — validación de dominio fallida
- `BusinessRuleError` — violación de regla de negocio

### 3. Tests

`tests/shared_kernel/test_value_objects.py` — 7 tests:
- Generación automática de UUID
- Aceptación de UUID explícito
- Igualdad y desigualdad
- Hash consistente
- Representación string y repr

`tests/shared_kernel/test_exceptions.py` — 5 tests:
- `DomainError` como `Exception`
- Formato de `NotFoundError`
- Jerarquía completa (`ValidationError`, `BusinessRuleError`)
- Todos atrapables como `DomainError`

### 4. Ejecución de tests

```
tests\shared_kernel\test_exceptions.py ...... PASSED [5/13]
tests\shared_kernel\test_value_objects.py .... PASSED [7/13]
tests\test_health.py ..................... PASSED [13/13]

13 passed in 0.90s
```

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `src/shared_kernel/domain/base_value_objects.py` | `EntityId` (UUID v4) |
| `src/shared_kernel/domain/base_exceptions.py` | Jerarquía de excepciones de dominio |
| `tests/shared_kernel/__init__.py` | Paquete de tests |
| `tests/shared_kernel/test_value_objects.py` | Tests de EntityId |
| `tests/shared_kernel/test_exceptions.py` | Tests de excepciones |

## Criterio de éxito

- ✅ Tests de creación de IDs únicos (UUID) — 7 tests pasando
- ✅ Tests de excepciones base del dominio — 5 tests pasando

## Próxima sesión

**Sesión 4: Tipos Primitivos (Objetos de Valor Genéricos)** — `Email`, `NotEmptyString`, `PositiveInt` en el Shared Kernel.
