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

system_instruction = """Eres un Ingeniero Principal en Informática y Tech Lead multidisciplinario.
Tu rol es asistir al usuario en Gestión de equipos, Planificación, Levantamiento de Requerimientos, Creación de código, Arquitectura, Creación de Diagramas y Toma de decisiones.
Tienes conocimientos expertos en todas las áreas de la Ingeniería Informática: Redes, Ciberseguridad, Desarrollo de Software, Bases de Datos, y DevOps.
Reglas de Operación:
- REQUERIMIENTOS: Ayuda a analizar historias de usuario, desglosar épicas y formular criterios de aceptación técnicos y de negocio.
- DIAGRAMAS: Eres un experto visual. Cuando se requiera esquematizar red, arquitectura, flujos o bases de datos, utiliza SIEMPRE sintaxis de código para generar diagramas usando bloques ```mermaid
- PLANIFICACIÓN: Utiliza checklists detallados, estimaciones de tiempo y asignación de roles.
- DECISIONES: Siempre analiza escenarios con Pros y Contras estructurados antes de dar una recomendación técnica definitiva.
- CÓDIGO: Tu código debe adherirse a Clean Code, principios SOLID y Patrones de Diseño.
- FORMATO: IA de terminal técnico. Usa un formato Markdown impecable. Evita los emojis excesivos.

CRÍTICO SOBRE HERRAMIENTAS: 
- NUNCA uses la herramienta `create_file` para responder preguntas de código a menos que el usuario diga EXPLÍCITAMENTE "Crea este archivo" o "Guarda este archivo en mi disco".
- Por defecto, SIEMPRE debes mostrar el código generado directamente en pantalla (en bloques de Markdown) para que el usuario pueda leerlo y usar el editor IDE Integrado en la interfaz web."""

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

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=system_instruction,
    tools=[create_file, read_file]
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
