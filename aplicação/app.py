from flask import Flask, render_template, request, jsonify, session
import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Garante que o diretório atual esteja no path para poder importar chatbot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import ChatbotService

app = Flask(__name__)
# Secret key para assinar os cookies de sessão
app.secret_key = os.urandom(24)

# Inicializa o serviço do chatbot
try:
    chatbot = ChatbotService()
except Exception as e:
    print(f"Erro ao inicializar ChatbotService: {e}")
    chatbot = None

@app.route('/')
def index():
    # Inicia a sessão zerada ou mantém a existente
    if 'historico' not in session:
        session['historico'] = []
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not chatbot:
        return jsonify({'response': "Erro: ChatbotService não está configurado corretamente (Verifique a API Key).", 'error': True}), 500

    data = request.json
    mensagem_usuario = data.get('message', '')

    if not mensagem_usuario:
        return jsonify({'response': "Mensagem vazia", 'error': True}), 400

    # Recupera o histórico da sessão
    historico = session.get('historico', [])

    try:
        # Chama o chatbot passando o histórico e a nova mensagem
        resposta = chatbot.enviar_mensagem(historico, mensagem_usuario)
        # Salva o histórico atualizado na sessão
        session['historico'] = historico
        return jsonify({'response': resposta})
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return jsonify({'response': f"Erro ao processar a mensagem: {e}", 'error': True}), 500

@app.route('/api/clear', methods=['POST'])
def clear_session():
    """Limpa o histórico do chat."""
    session['historico'] = []
    return jsonify({'success': True})

if __name__ == '__main__':
    # Roda o servidor Flask na porta 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
