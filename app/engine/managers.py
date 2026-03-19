import os
import json
from config import BASE_DIR, VECTOR_DB_DIR
from app.engine.vectordb import VectorDB

class ContextManager:
    """Gestiona la carga e inyección de contexto usando RAG (Vector DB)."""
    def __init__(self, context_dir: str):
        self.context_dir = context_dir
        self.db_path = VECTOR_DB_DIR
        self.vdb = VectorDB(self.db_path)
        self._index_context()

    def _index_context(self):
        """Escanea archivos y actualiza la base de datos vectorial."""
        if not os.path.isdir(self.context_dir):
            return

        docs = []
        ids = []
        metadatas = []
        
        for filename in os.listdir(self.context_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(self.context_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if content:
                        docs.append(content)
                        ids.append(filename)
                        metadatas.append({"source": filename})
                except Exception as e:
                    print(f"Error indexando {filename}: {e}")
        
        if docs:
            self.vdb.add_documents(docs, ids, metadatas)

    def load_all(self) -> str:
        """Carga todo el contexto para el prompt del sistema inicial."""
        context_blocks = []
        if os.path.isdir(self.context_dir):
            for filename in sorted(os.listdir(self.context_dir)):
                if filename.endswith(".md"):
                    filepath = os.path.join(self.context_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        context_blocks.append(f"### {filename}\n{f.read()}")
        return "\n\n".join(context_blocks)

    def search(self, query: str) -> str:
        """Busca fragmentos relevantes usando RAG."""
        return self.vdb.query(query, n_results=3)

class HistoryManager:
    """Gestiona la persistencia y carga del historial de chat."""
    def __init__(self, history_file: str):
        self.history_file = history_file

    def load(self) -> list:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando historial: {e}")
        return []

    def save(self, chat_session):
        try:
            history_entries = []
            for message in chat_session.history:
                parts = []
                for part in message.parts:
                    if hasattr(part, 'text') and part.text:
                        parts.append({"text": part.text})
                    elif hasattr(part, 'function_call') and part.function_call:
                        parts.append({
                            "function_call": {
                                "name": part.function_call.name,
                                "args": dict(part.function_call.args)
                            }
                        })
                    elif hasattr(part, 'function_response') and part.function_response:
                        parts.append({
                            "function_response": {
                                "name": part.function_response.name,
                                "response": dict(part.function_response.response)
                            }
                        })
                history_entries.append({
                    "role": message.role,
                    "parts": parts
                })
            
            # Asegurar que la carpeta data/ existe
            os.makedirs(os.path.dirname(os.path.abspath(self.history_file)), exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history_entries, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def clear(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
