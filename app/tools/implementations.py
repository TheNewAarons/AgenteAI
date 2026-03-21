import os
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
import logging
from config import CONTEXT_DIR
from . import tool
from .security import is_safe_path

# Configuración básica de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@tool
def plan_tasks(tasks: list) -> str:
    """Define un plan de sub-tareas para resolver un objetivo complejo.
    Args:
        tasks: Lista de strings con las descripciones de las tareas (ej: ["Crear modelo", "Añadir tests"]).
    """
    from config import DATA_DIR
    from app.engine.managers import TaskManager
    tm = TaskManager(os.path.join(DATA_DIR, "tasks.json"))
    tm.add_tasks(tasks)
    return f"Plan of {len(tasks)} tasks registered."

@tool
def update_task_status(task_id: int, status: str, result: str = "") -> str:
    """Actualiza el estado de una sub-tarea.
    Args:
        task_id: El ID numérico de la tarea.
        status: El nuevo estado (Pendiente, En Progreso, Completado, Fallido).
        result: Breve resumen del resultado de la tarea.
    """
    from config import DATA_DIR
    from app.engine.managers import TaskManager
    tm = TaskManager(os.path.join(DATA_DIR, "tasks.json"))
    tm.update_task(task_id, status, result)
    return f"Task {task_id} updated to {status}."

@tool
def get_tasks() -> str:
    """Retorna la lista actual de sub-tareas y su estado."""
    from config import DATA_DIR
    from app.engine.managers import TaskManager
    tm = TaskManager(os.path.join(DATA_DIR, "tasks.json"))
    tasks = tm.load()
    if not tasks: return "No tasks planned."
    
    res = ["### Plan de Trabajo Actual:"]
    for t in tasks:
        res.append(f"{t['id']}. [{t['status']}] {t['description']}")
    return "\n".join(res)

@tool
def create_file(path: str, content: str) -> str:
    """Crea un nuevo archivo en la ruta especificada con el contenido dado.
    Args:
        path: Ruta donde se debe crear el archivo.
        content: El contenido de texto a escribir en el archivo.
    """
    if not is_safe_path(path):
        return f"ERROR: Access denied. Path {path} is prohibited."
    
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {path} created."
    except Exception as e:
        logger.error(f"Error creating file {path}: {e}")
        return f"Error creating file {path}: {str(e)}"

@tool
def read_file(path: str) -> str:
    """Lee el contenido de un archivo en la ruta especificada.
    Args:
        path: Ruta del archivo a leer.
    """
    if not is_safe_path(path):
        return f"ERROR: Access denied. Path {path} is prohibited."
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return f"Error reading file {path}: {str(e)}"

@tool
def run_python_code(code: str) -> str:
    """Ejecuta código Python en un subproceso y retorna el output.
    Args:
        code: El string de código Python a ejecutar.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout or ""
        errors = result.stderr or ""
        if errors:
            return f"OUTPUT:\n{output}\nERRORS:\n{errors}" if output else f"ERROR:\n{errors}"
        return f"OUTPUT:\n{output}" if output else "(No output)"
    except subprocess.TimeoutExpired:
        return "ERROR: Execution timeout (15s)."
    except Exception as e:
        return f"ERROR executing code: {str(e)}"

@tool
def run_command(command: str) -> str:
    """Ejecuta un comando del sistema (bash/shell) y retorna su salida.
    Usa esto para tareas de terminal como listar archivos (ls), ver estado de git, etc.
    Args:
        command: El comando a ejecutar (ej: 'ls -R', 'git status').
    """
    # Lista negra de comandos peligrosos
    forbidden = ["rm ", "sudo ", "chmod ", "chown ", "mv /", "del "]
    if any(cmd in command.lower() for cmd in forbidden):
        return "ERROR: Command blocked for security."

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=20
        )
        output = result.stdout or ""
        errors = result.stderr or ""
        if errors:
            return f"STDOUT:\n{output}\nSTDERR:\n{errors}" if output else f"STDERR:\n{errors}"
        return f"STDOUT:\n{output}" if output else "(Success)"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timeout (20s)."
    except Exception as e:
        logger.error(f"Error executing command '{command}': {e}")
        return f"ERROR executing command: {str(e)}"

@tool
def list_directory(path: str = ".") -> str:
    """Lista la estructura de archivos y carpetas de un directorio.
    Args:
        path: La ruta del directorio a listar.
    """
    if not is_safe_path(path):
        return f"ERROR: Access denied. Path {path} is prohibited."

    try:
        exclude = ["venv", "__pycache__", ".git", "node_modules", ".DS_Store"]
        result = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in exclude]
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * level
            result.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                if f not in exclude:
                    result.append(f"{sub_indent}{f}")
        return "\n".join(result)
    except Exception as e:
        return f"ERROR listing directory: {str(e)}"

@tool
def fetch_url(url: str) -> str:
    """Obtiene el contenido de una URL y lo convierte a texto plano legible.
    Args:
        url: La dirección web a consultar.
    """
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]
    except Exception as e:
        return f"ERROR fetching URL {url}: {str(e)}"

@tool
def search_context(keyword: str) -> str:
    """Searches keyword in project context files."""
    results = []
    if os.path.isdir(CONTEXT_DIR):
        for filename in sorted(os.listdir(CONTEXT_DIR)):
            if filename.endswith(".md"):
                filepath = os.path.join(CONTEXT_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    matches = [
                        f"  Line {i+1}: {line.rstrip()}"
                        for i, line in enumerate(lines)
                        if keyword.lower() in line.lower()
                    ]
                    if matches:
                        results.append(f"[{filename}]\n" + "\n".join(matches))
                except Exception as e:
                    results.append(f"[{filename}] ERROR: {e}")
    return "\n\n".join(results) if results else f"No matches found for '{keyword}'."

