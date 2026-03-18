import os
import json
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, CONTEXT_DIR, HISTORY_FILE, MODEL_NAME
from core.tools import ALL_TOOLS

class AIAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no configurada.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=self._build_system_prompt(),
            tools=ALL_TOOLS
        )
        self.chat_session = None
        self._load_session()

    def _load_context_files(self) -> str:
        """Lee todos los archivos .md de project-context/."""
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

    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema base + contexto del usuario."""
        context = self._load_context_files()
        
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
- Identifícate como el Agente Modular v2."""

        if context:
            base_prompt += f"\n\n---\n\n## CONTEXTO DINÁMICO DEL USUARIO\n\n{context}"
        
        return base_prompt

    def _load_session(self):
        """Inicializa o recupera la sesión de chat con el historial guardado."""
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                print(f"Error cargando historial: {e}")

        # Iniciar chat SIN automatic function calling para permitir streaming real
        self.chat_session = self.model.start_chat(
            history=history,
            enable_automatic_function_calling=False
        )

    def save_history(self):
        """Persiste el historial actual en el archivo JSON."""
        try:
            history_entries = []
            for message in self.chat_session.history:
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
            
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history_entries, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def send_message(self, message: str, stream=True):
        """Envía un mensaje al modelo y maneja manualmente el bucle de herramientas."""
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
        """Reinicia el chat y borra el archivo de historial."""
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self._load_session()
