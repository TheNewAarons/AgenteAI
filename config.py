import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Rutas y Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Desactivar telemetría de ChromaDB globalmente
os.environ["ANONYMIZED_TELEMETRY"] = "False"

CONTEXT_DIR = os.path.join(BASE_DIR, "project-context")
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
VECTOR_DB_DIR = os.path.join(DATA_DIR, ".vector_db")

# Configuración del Agente
MODEL_NAME = 'gemini-2.5-flash'
APP_PORT = 5001
DEBUG_MODE = True
