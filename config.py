import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Rutas y Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTEXT_DIR = os.path.join(BASE_DIR, "project-context")
HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")

# Configuración del Agente
MODEL_NAME = 'gemini-2.5-flash'
APP_PORT = 5000
DEBUG_MODE = True
