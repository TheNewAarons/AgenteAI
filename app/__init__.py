from flask import Flask
from config import DEBUG_MODE
from .api.routes import main_bp

def create_app():
    app = Flask(__name__)
    
    # Registrar Blueprints
    app.register_blueprint(main_bp)
    
    return app
