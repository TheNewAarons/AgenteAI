from flask import Flask
from config import APP_PORT, DEBUG_MODE
from core.routes import main_bp

def create_app():
    app = Flask(__name__)
    
    # Registrar Blueprints
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"[AgenteAI] Iniciando servidor en http://127.0.0.1:{APP_PORT}")
    app.run(debug=DEBUG_MODE, port=APP_PORT)
