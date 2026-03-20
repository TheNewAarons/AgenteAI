import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME, CONTEXT_DIR, HISTORY_FILE
from app.tools import ALL_TOOLS
from .managers import ContextManager, HistoryManager

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
- Identifícate como el Agente Modular v3.0-PRO."""

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

    def send_message(self, message: str, stream=True, _recursion_limit=5):
        """Envía un mensaje al modelo, inyectando contexto relevante vía RAG."""
        if _recursion_limit <= 0:
            yield "ERROR: Se ha alcanzado el límite de recursión en llamadas a herramientas."
            return

        # 1. RAG: Buscar contexto si es un mensaje de texto (no una respuesta de herramienta)
        if isinstance(message, str):
            context_fragment = self.context_mgr.search(message)
            if context_fragment:
                message = f"[CONTEXTO RELEVANTE]\n{context_fragment}\n\n[MENSAJE USUARIO]\n{message}"

        try:
            response = self.chat_session.send_message(message, stream=stream)
        except Exception as e:
            error_msg = f"Error en la comunicación con el modelo: {str(e)}"
            if stream:
                yield error_msg
                return
            return error_msg
        
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
                            try:
                                result = tool_fn(**fn_args)
                            except Exception as e:
                                result = f"Error ejecutando la herramienta {fn_name}: {str(e)}"
                            
                            # Enviar la respuesta de la herramienta de vuelta al modelo
                            # Y RECURSIVAMENTE obtener el resto de la respuesta (streaming)
                            tool_response = {
                                'function_response': {
                                    'name': fn_name,
                                    'response': {'result': result}
                                }
                            }
                            
                            # Continuar el flujo enviando la respuesta de vuelta
                            for sub_chunk in self.send_message(tool_response, stream=True, _recursion_limit=_recursion_limit-1):
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
                            try:
                                result = tool_fn(**fn_args)
                            except Exception as e:
                                result = f"Error ejecutando la herramienta {fn_name}: {str(e)}"

                            tool_response_part = {
                                'function_response': {
                                    'name': fn_name,
                                    'response': {'result': result}
                                }
                            }
                            return self.send_message(tool_response_part, stream=False, _recursion_limit=_recursion_limit-1)
            
            self.save_history()
            return response.text

    def clear_history(self):
        """Reinicia el chat y borra el historial."""
        self.history_mgr.clear()
        self._load_session()
