import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.environ["ANONYMIZED_TELEMETRY"] = "False"

CONTEXT_DIR = os.path.join(BASE_DIR, "project-context")
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
VECTOR_DB_DIR = os.path.join(DATA_DIR, ".vector_db")

MODEL_NAME = 'gemini-2.5-flash'
APP_PORT = 5001
DEBUG_MODE = True
