import logging

logger = logging.getLogger(__name__)

# Lista global de herramientas registradas
ALL_TOOLS = []

def tool(fn):
    """Decorador para registrar una función como herramienta del agente."""
    if fn not in ALL_TOOLS:
        ALL_TOOLS.append(fn)
    return fn

# Cargar las implementaciones para registrar las herramientas
from . import implementations
