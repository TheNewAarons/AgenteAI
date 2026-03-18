import os
import sys
from core.agent_engine import AIAgent

def agente_cli():
    print("🤖 --- AgenteAI CLI (v2.5) ---")
    print("Iniciando motor de IA...")
    
    try:
        agent = AIAgent()
        print("🤖 ¡Listo! Escribe 'salir' para terminar.")
    except Exception as e:
        print(f"❌ Error al inicializar el agente: {e}")
        return

    while True:
        try:
            user_input = input("\nTú: ")
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("🤖 ¡Hasta luego!")
                break
                
            if not user_input.strip():
                continue
                
            # Enviamos el mensaje al modelo con streaming desactivado para consola
            print("\n🤖 Agente: ", end="", flush=True)
            for chunk in agent.send_message(user_input, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
            
        except KeyboardInterrupt:
            print("\n🤖 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    agente_cli()
