import logging

logger = logging.getLogger(__name__)

# Lista global de herramientas registradas
ALL_TOOLS = []

def tool(fn):
    """Decorator to register function as agent tool."""
    if fn not in ALL_TOOLS:
        ALL_TOOLS.append(fn)
    return fn

# Cargar las implementaciones para registrar las herramientas
from . import implementations
