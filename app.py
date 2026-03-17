import os
import json
from flask import Flask, request, jsonify, render_template, Response
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar la API key de Gemini
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la API Key. Por favor agrégala en el archivo .env")

genai.configure(api_key=api_key)

CONTEXT_DIR = "project-context"

def load_context_files() -> str:
    """Lee todos los archivos .md de project-context/ y los concatena como contexto."""
    context_blocks = []
    if os.path.isdir(CONTEXT_DIR):
        for filename in sorted(os.listdir(CONTEXT_DIR)):
            if filename.endswith(".md"):
                filepath = os.path.join(CONTEXT_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    context_blocks.append(f"### {filename}\n{content}")
                except Exception as e:
                    print(f"Error leyendo contexto {filename}: {e}")
    return "\n\n".join(context_blocks)

def build_system_prompt() -> str:
    """Construye el system prompt completo inyectando el contexto del usuario."""
    context = load_context_files()

    base_prompt = """Eres un Ingeniero Principal en Informática y Tech Lead multidisciplinario altamente especializado.
Tu objetivo es ser el asistente técnico de cabecera del usuario en TODAS las fases de un proyecto de Ingeniería Informática.

## ROL Y CAPACIDADES

### Levantamiento de Requerimientos
- Analiza necesidades de negocio y técnicas.
- Desglosa épicas en Historias de Usuario (formato: "Como [rol], quiero [acción] para [beneficio]").
- Formula Criterios de Aceptación técnicos y funcionales.
- Identifica Requisitos No Funcionales: rendimiento, seguridad, escalabilidad.

### Planificación y Gestión
- Propón roadmaps con fases, hitos y estimaciones de tiempo realistas.
- Crea checklists detallados por fase del proyecto.
- Sugiere asignación de roles según habilidades del equipo.
- Usa metodologías ágiles (Scrum, Kanban) y estima en Story Points cuando sea útil.

### Arquitectura y Toma de Decisiones
- Diseña arquitecturas: monolito, microservicios, serverless, event-driven.
- Antes de recomendar tecnología: presenta análisis de Pros y Contras estructurado.
- Recomienda patrones de diseño (Factory, Repository, Observer, etc.) cuando aplique.

### Diagramas Técnicos
- SIEMPRE usa bloques ```mermaid para generar diagramas cuando se solicite visualizar algo.
- Tipos soportados: Flowchart, Sequence, ER, Class, Gantt, C4.

### Generación de Código
- Genera código limpio siguiendo las guías de estilo del usuario (ver contexto personalizado).
- Principios obligatorios: Clean Code, SOLID, DRY, KISS.
- Muestra el código SIEMPRE en bloques Markdown en pantalla.
- NUNCA uses create_file a menos que el usuario lo pida explícitamente con "guarda" o "crea el archivo".

### Dominios de Expertise
- Desarrollo de Software Full Stack
- Bases de Datos relacionales y NoSQL
- Redes y Telecomunicaciones
- Ciberseguridad (OWASP, hardening, análisis de vulnerabilidades)
- DevOps: CI/CD, contenedores, Infrastructure as Code

## REGLAS DE FORMATO
- Responde siempre en Español (Chile).
- Usa Markdown estructurado con encabezados, listas y tablas.
- Sé directo y técnico. Sin relleno ni frases genéricas.
- Para código, usa siempre bloques con el lenguaje especificado (```python, ```js, etc.)."""

    if context:
        base_prompt += f"\n\n---\n\n## CONTEXTO PERSONALIZADO DEL USUARIO\n\nEl siguiente contexto define quién es el usuario, su stack tecnológico y sus preferencias de código. Úsalo en TODAS tus respuestas.\n\n{context}"

    return base_prompt

system_instruction = build_system_prompt()
print(f"[AI Agent] System prompt cargado ({len(system_instruction)} chars)")
if os.path.isdir(CONTEXT_DIR):
    ctx_files = [f for f in os.listdir(CONTEXT_DIR) if f.endswith(".md")]
    print(f"[AI Agent] Contexto cargado: {', '.join(ctx_files)}")

def create_file(path: str, content: str) -> str:
    """Creates a new file at the specified path with the given content. Use this to save code.
    Args:
        path: Path where the file should be created.
        content: The text content to write into the file.
    """
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"File {path} created successfully."
    except Exception as e:
        return f"Error creating file {path}: {str(e)}"

def read_file(path: str) -> str:
    """Reads the content of a file at the specified path. Use this to review code before changing it.
    Args:
        path: Path of the file to read.
    """
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def run_python_code(code: str) -> str:
    """Executes Python code in a sandboxed subprocess and returns stdout/stderr.
    Use this to test algorithms, verify logic, or demonstrate outputs from user requests.
    Args:
        code: The Python code string to execute.
    """
    import subprocess, sys
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout or ""
        errors = result.stderr or ""
        if errors:
            return f"OUTPUT:\n{output}\nERRORS:\n{errors}" if output else f"ERROR:\n{errors}"
        return f"OUTPUT:\n{output}" if output else "(No output produced)"
    except subprocess.TimeoutExpired:
        return "ERROR: Execution timed out after 10 seconds."
    except Exception as e:
        return f"ERROR running code: {str(e)}"

def list_directory(path: str = ".") -> str:
    """Lists the file and folder structure of a directory. Use this to understand project layout.
    Args:
        path: The directory path to list. Defaults to the current project directory.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["find", path, "-not", "-path", "*/\\.*", "-not", "-path", "*/venv/*",
             "-not", "-path", "*/__pycache__/*", "-not", "-name", "*.pyc"],
            capture_output=True, text=True, timeout=5
        )
        lines = sorted(result.stdout.strip().split("\n"))
        return "\n".join(lines) if lines else "(empty directory)"
    except Exception as e:
        return f"ERROR listing directory: {str(e)}"

def search_context(keyword: str) -> str:
    """Searches for a keyword across all project context files in project-context/.
    Use this to retrieve specific known preferences, stack info, or code rules.
    Args:
        keyword: The keyword to search for.
    """
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

# Usaremos el modelo gemini-1.5-flash por ser rápido y eficiente
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=system_instruction,
    tools=[create_file, read_file, run_python_code, list_directory, search_context]
)

# Diccionario para almacenar historiales de chat por sesión o usuario
chats = {}

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
    return []

def save_chat_history(chat):
    try:
        history_data = []
        for message in chat.history:
            parts = []
            for part in message.parts:
                if hasattr(part, 'text') and part.text:
                    parts.append({"text": part.text})
                elif hasattr(part, 'function_call'):
                    parts.append({
                        "function_call": {
                            "name": part.function_call.name,
                            "args": dict(part.function_call.args)
                        }
                    })
                elif hasattr(part, 'function_response'):
                    parts.append({
                        "function_response": {
                            "name": part.function_response.name,
                            "response": dict(part.function_response.response)
                        }
                    })
            
            history_data.append({
                "role": message.role,
                "parts": parts
            })
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")

def get_chat(session_id="default"):
    if session_id not in chats:
        raw_history = load_history()
        formatted_history = []
        for msg in raw_history:
            formatted_history.append({
                "role": msg["role"],
                "parts": msg["parts"]
            })
        chats[session_id] = model.start_chat(
            history=formatted_history,
            enable_automatic_function_calling=True
        )
    return chats[session_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    chat = get_chat()
    
    def generate():
        try:
            # Gemini SDK no soporta stream=True junto a enable_automatic_function_calling=True
            # Por ende, pedimos la respuesta sin stream y simulamos el streaming hacia el frontend
            import time
            response = chat.send_message(user_message, stream=False)
            
            if response.text:
                chunk_size = 15
                for i in range(0, len(response.text), chunk_size):
                    chunk = response.text[i:i+chunk_size]
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    time.sleep(0.01)
            
            save_chat_history(chat)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

@app.route('/clear_history', methods=['POST'])
def clear_history():
    # Reiniciar el chat creando uno nuevo con historial vacío
    chats["default"] = model.start_chat(history=[])
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    print("Iniciando el servidor del Terminal AI en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
