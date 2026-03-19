import os
import logging
from config import BASE_DIR

logger = logging.getLogger(__name__)

def is_safe_path(path: str) -> bool:
    """Verifica si una ruta está dentro del directorio base del proyecto."""
    try:
        abs_base = os.path.abspath(BASE_DIR)
        abs_target = os.path.abspath(os.path.join(abs_base, path))
        return abs_target.startswith(abs_base)
    except Exception as e:
        logger.error(f"Error validando ruta {path}: {e}")
        return False
