from app import create_app
from config import APP_PORT, DEBUG_MODE

app = create_app()

if __name__ == '__main__':
    print(f"[AgenteAI] Iniciando servidor en http://0.0.0.0:{APP_PORT}")
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=APP_PORT)
