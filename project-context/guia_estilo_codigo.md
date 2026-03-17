# Guía de Estilo de Código

## Principios Generales
- **Clean Code**: El código debe ser legible, expresivo y autodocumentado.
- **SOLID**: Aplicar los 5 principios en toda arquitectura orientada a objetos.
- **DRY** (Don't Repeat Yourself): Sin duplicación de lógica.
- **KISS** (Keep It Simple, Stupid): Preferir la solución más simple que funcione.

## Python

### Convenciones
- Seguir **PEP 8** estrictamente
- Nombres de variables y funciones: `snake_case`
- Nombres de clases: `PascalCase`
- Constantes: `UPPER_CASE`
- Comentarios: Solo cuando la lógica no sea obvia
- Docstrings: Obligatorios en funciones públicas (formato Google style)

### Estructura de Funciones
```python
def nombre_funcional(param: tipo) -> tipo_retorno:
    """Descripción breve de la función.
    
    Args:
        param: Descripción del parámetro.
    
    Returns:
        Descripción de lo que retorna.
    """
    pass
```

### Manejo de Errores
- Usar `try/except` específico, nunca capturar `Exception` genérica sin razón.
- Siempre loguear errores con `print` o `logging`.

## JavaScript

### Convenciones
- Variables y funciones: `camelCase`
- Clases: `PascalCase`
- Usar `const` por defecto, `let` cuando sea necesario. Nunca `var`.
- Arrow functions para callbacks.
- Separar lógica en funciones pequeñas y bien nombradas.

## SQL
- Palabras clave en MAYÚSCULAS: `SELECT`, `FROM`, `WHERE`
- Nombres de tablas y columnas en `snake_case`
- Siempre usar índices en columnas de búsqueda frecuente

## Git y Control de Versiones
- **Commits**: Usar Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- **Ramas**: `feature/nombre-feature`, `fix/nombre-bug`, `release/v1.0`
- Nunca hacer commit directo a `main`

## Documentación
- Todo proyecto debe tener un `README.md` detallado
- Documentar APIs con comentarios o herramientas como Swagger
- Usar Mermaid para diagramas en documentación técnica
