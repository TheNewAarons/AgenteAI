import os
import logging
from config import BASE_DIR

logger = logging.getLogger(__name__)

def is_safe_path(path: str) -> bool:
    """Validates if path is within project base directory."""
    try:
        abs_base = os.path.abspath(BASE_DIR)
        abs_target = os.path.abspath(os.path.join(abs_base, path))
        return abs_target.startswith(abs_base)
    except Exception as e:
        logger.error(f"Path validation error {path}: {e}")
        return False
