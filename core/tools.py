import os
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
from config import CONTEXT_DIR

def create_file(path: str, content: str) -> str:
    """Crea un nuevo archivo en la ruta especificada con el contenido dado.
    Args:
        path: Ruta donde se debe crear el archivo.
        content: El contenido de texto a escribir en el archivo.
    """
    try:
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Archivo {path} creado exitosamente."
    except Exception as e:
        return f"Error al crear el archivo {path}: {str(e)}"

def read_file(path: str) -> str:
    """Lee el contenido de un archivo en la ruta especificada.
    Args:
        path: Ruta del archivo a leer.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer el archivo {path}: {str(e)}"

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
        return f"OUTPUT:\n{output}" if output else "(Sin salida producida)"
    except subprocess.TimeoutExpired:
        return "ERROR: La ejecución excedió el tiempo límite de 15 segundos."
    except Exception as e:
        return f"ERROR ejecutando código: {str(e)}"

def run_command(command: str) -> str:
    """Ejecuta un comando del sistema (bash/shell) y retorna su salida.
    Usa esto para tareas de terminal como listar archivos (ls), ver estado de git, etc.
    Args:
        command: El comando a ejecutar (ej: 'ls -R', 'git status').
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=20
        )
        output = result.stdout or ""
        errors = result.stderr or ""
        if errors:
            return f"STDOUT:\n{output}\nSTDERR:\n{errors}" if output else f"STDERR:\n{errors}"
        return f"STDOUT:\n{output}" if output else "(Comando ejecutado sin salida)"
    except subprocess.TimeoutExpired:
        return "ERROR: El comando excedió el tiempo límite de 20 segundos."
    except Exception as e:
        return f"ERROR ejecutando comando: {str(e)}"

def list_directory(path: str = ".") -> str:
    """Lista la estructura de archivos y carpetas de un directorio.
    Args:
        path: La ruta del directorio a listar.
    """
    try:
        # Excluir directorios pesados o irrelevantes
        exclude = ["venv", "__pycache__", ".git", "node_modules", ".DS_Store"]
        result = []
        for root, dirs, files in os.walk(path):
            # Modificar dirs in-place para saltar los excluidos
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
        return f"ERROR listando directorio: {str(e)}"

def fetch_url(url: str) -> str:
    """Obtiene el contenido de una URL y lo convierte a texto plano legible.
    Args:
        url: La dirección web a consultar.
    """
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Limpiar scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator='\n')
        # Limpiar espacios en blanco
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:10000] # Limitar a 10k caracteres para el contexto de la IA
    except Exception as e:
        return f"ERROR al obtener URL {url}: {str(e)}"

def search_context(keyword: str) -> str:
    """Busca una palabra clave en los archivos de proyecto-context/."""
    results = []
    if os.path.isdir(CONTEXT_DIR):
        for filename in sorted(os.listdir(CONTEXT_DIR)):
            if filename.endswith(".md"):
                filepath = os.path.join(CONTEXT_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    matches = [
                        f"  Línea {i+1}: {line.rstrip()}"
                        for i, line in enumerate(lines)
                        if keyword.lower() in line.lower()
                    ]
                    if matches:
                        results.append(f"[{filename}]\n" + "\n".join(matches))
                except Exception as e:
                    results.append(f"[{filename}] ERROR: {e}")
    return "\n\n".join(results) if results else f"No se encontraron coincidencias para '{keyword}'."

# Lista de herramientas para ser exportada
ALL_TOOLS = [create_file, read_file, run_python_code, run_command, list_directory, fetch_url, search_context]
