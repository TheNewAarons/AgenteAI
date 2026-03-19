import os
import json
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, CONTEXT_DIR, HISTORY_FILE, MODEL_NAME, BASE_DIR, VECTOR_DB_DIR
from app.tools import ALL_TOOLS
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
                        # Si el archivo es muy grande, se podría fragmentar. 
                        # Por ahora, un archivo = un documento para mantenerlo simple.
                        docs.append(content)
                        ids.append(filename)
                        metadatas.append({"source": filename})
                except Exception as e:
                    print(f"Error indexando {filename}: {e}")
        
        if docs:
            self.vdb.add_documents(docs, ids, metadatas)

    def load_all(self) -> str:
        """Fallback: Carga todo el contexto (puedes usarlo para debugging)."""
        # (Se mantiene igual por compatibilidad si es necesario, pero AIAgent usará search)
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
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history_entries, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def clear(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

class AIAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no configurada.")
        
        self.context_mgr = ContextManager(CONTEXT_DIR)
        self.history_mgr = HistoryManager(HISTORY_FILE)
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=self._build_system_prompt(),
            tools=ALL_TOOLS
        )
        self.chat_session = None
        self._load_session()

    def _build_system_prompt(self, user_query: str = "") -> str:
        """Construye el prompt del sistema base + fragmentos RAG."""
        # Si no hay query (inicio), cargamos una visión general o nada
        context = ""
        if user_query:
            context = self.context_mgr.search(user_query)
        else:
            # Al inicio, cargar solo los perfiles básicos si existen
            context = self.context_mgr.load_all() # O un subconjunto
        
        base_prompt = """Eres un Ingeniero Principal en Informática y Tech Lead multidisciplinario altamente especializado.
Tu objetivo es ser el asistente técnico de cabecera del usuario en TODAS las fases de un proyecto de software.

## ROL Y CAPACIDADES
- Levantamiento de Requerimientos: Analiza necesidades, desglosa épicas en Historias de Usuario con Criterios de Aceptación técnicos.
- Planificación: Propón roadmaps, estimaciones realistas y checklists por fase.
- Arquitectura: Diseña sistemas escalables (Monolitos, Microservicios). Antes de elegir tecnología, presenta Pros/Contras.
- Diagramas: SIEMPRE usa bloques ```mermaid para visualizar flujos, secuencias, ER, C4, etc.
- Generación de Código: Sigue las guías de estilo del usuario (Clean Code, SOLID). Especialista en Full Stack, DBs, Ciberseguridad y DevOps.
- Herramientas de Terminal: Puedes ejecutar comandos bash reales, leer archivos, crear archivos y buscar contexto.

## REGLAS DE ORO
- Responde siempre en Español (Chile).
- Sé directo, técnico y evita relleno.
- Usa bloques de código con lenguaje especificado (```python, ```js, etc.).
- Identifícate como el Agente Modular v2.0-Refactored."""

        if context:
            base_prompt += f"\n\n---\n\n## CONTEXTO DINÁMICO DEL USUARIO\n\n{context}"
        
        return base_prompt

    def _load_session(self):
        """Inicializa o recupera la sesión de chat con el historial guardado."""
        history = self.history_mgr.load()
        self.chat_session = self.model.start_chat(
            history=history,
            enable_automatic_function_calling=False
        )

    def save_history(self):
        self.history_mgr.save(self.chat_session)

    def send_message(self, message: str, stream=True):
        """Envía un mensaje al modelo, inyectando contexto relevante vía RAG."""
        
        # 1. RAG: Buscar contexto si es un mensaje de texto (no una respuesta de herramienta)
        if isinstance(message, str):
            context_fragment = self.context_mgr.search(message)
            if context_fragment:
                message = f"[CONTEXTO RELEVANTE]\n{context_fragment}\n\n[MENSAJE USUARIO]\n{message}"

        response = self.chat_session.send_message(message, stream=stream)
        
        if stream:
            for chunk in response:
                # Si el chunk tiene texto, lo emitimos
                try:
                    if chunk.text:
                        yield chunk.text
                except:
                    # A veces el chunk no tiene texto si es una function_call
                    pass
                
                # Revisar si hay llamadas a funciones en este chunk
                for part in chunk.parts:
                    if part.function_call:
                        # Ejecutar la herramienta
                        fn_name = part.function_call.name
                        fn_args = part.function_call.args
                        
                        # Buscar la función en nuestras herramientas
                        tool_fn = next((t for t in ALL_TOOLS if t.__name__ == fn_name), None)
                        if tool_fn:
                            result = tool_fn(**fn_args)
                            
                            # Enviar la respuesta de la herramienta de vuelta al modelo
                            # Y RECURSIVAMENTE obtener el resto de la respuesta (streaming)
                            tool_response = {
                                'function_response': {
                                    'name': fn_name,
                                    'response': {'result': result}
                                }
                            }
                            
                            # Continuar el flujo enviando la respuesta de vuelta
                            for sub_chunk in self.send_message(tool_response, stream=True):
                                yield sub_chunk
            self.save_history()
        else:
            # Lógica no-stream (bucle manual)
            if response.parts:
                for part in response.parts:
                    if part.function_call:
                        fn_name = part.function_call.name
                        fn_args = part.function_call.args
                        tool_fn = next((t for t in ALL_TOOLS if t.__name__ == fn_name), None)
                        if tool_fn:
                            result = tool_fn(**fn_args)
                            tool_response_part = {
                                'function_response': {
                                    'name': fn_name,
                                    'response': {'result': result}
                                }
                            }
                            return self.send_message(tool_response_part, stream=False)
            
            self.save_history()
            return response.text

    def clear_history(self):
        """Reinicia el chat y borra el historial."""
        self.history_mgr.clear()
        self._load_session()
