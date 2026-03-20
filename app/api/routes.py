import json
from flask import Blueprint, request, jsonify, render_template, Response, stream_with_context
from app.engine.agent import AIAgent

main_bp = Blueprint('main', __name__)
agent = None

def get_agent():
    global agent
    if agent is None:
        agent = AIAgent()
    return agent

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    agent_instance = get_agent()
    def generate_response():
        try:
            # Iteramos sobre el generador de streaming real de AIAgent
            for text_chunk in agent_instance.send_message(user_message, stream=True):
                yield f"data: {json.dumps({'chunk': text_chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return Response(generate_response(), mimetype='text/event-stream')

@main_bp.route('/clear_history', methods=['POST'])
def clear_history():
    get_agent().clear_history()
    return jsonify({"status": "success", "message": "Historial borrado correctamente"})

@main_bp.route('/list_files', methods=['GET'])
def list_files():
    from app.tools.implementations import list_directory
    path = request.args.get('path', '.')
    structure = list_directory(path)
    return jsonify({"structure": structure})

@main_bp.route('/save_file', methods=['POST'])
def save_file():
    from app.tools.implementations import create_file
    data = request.json
    path = data.get('path')
    content = data.get('content')
    if not path or content is None:
        return jsonify({"error": "Faltan datos"}), 400
    
    result = create_file(path, content)
    return jsonify({"message": result})
