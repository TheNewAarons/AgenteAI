import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configurar la API key de Gemini
# Buscamos GEMINI_API_KEY o OPENAI_API_KEY por si cambiaste el nombre o lo dejaste igual
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ No se encontró la API Key. Por favor agrégala en el archivo .env")
    exit(1)

genai.configure(api_key=api_key)

# Usaremos el modelo gemini-2.5-flash por ser rápido y eficiente
model = genai.GenerativeModel('gemini-2.5-flash')

def agente_basico():
    print("🤖 Hola, soy tu agente de IA impulsado por Google Gemini. Escribe 'salir' para terminar.")
    
    # Iniciamos sesión de chat para mantener el contexto
    try:
        chat = model.start_chat(history=[])
    except Exception as e:
        print(f"❌ Error al inicializar el modelo: {e}")
        return

    while True:
        try:
            user_input = input("\nTú: ")
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("🤖 ¡Hasta luego!")
                break
                
            if not user_input.strip():
                continue
                
            # Enviamos el mensaje al modelo y obtenemos respuesta
            response = chat.send_message(user_input)
            
            print(f"\n🤖 Agente:\n{response.text}")
            
        except Exception as e:
            print(f"\n❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    agente_basico()
