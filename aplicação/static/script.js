document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearBtn = document.getElementById('clear-btn');
    const initialTime = document.getElementById('initial-time');

    // Configura a hora inicial
    const now = new Date();
    initialTime.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Rolar para baixo ao carregar
    scrollToBottom();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Adiciona a mensagem do usuário na tela
        appendMessage('user', message);
        
        // Limpa o input
        userInput.value = '';
        
        // Mostra o indicador de digitação
        showTypingIndicator();

        try {
            // Envia para o Backend Flask
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Esconde o indicador e mostra a resposta do bot
            hideTypingIndicator();
            appendMessage('bot', data.response);

        } catch (error) {
            console.error('Erro:', error);
            hideTypingIndicator();
            appendMessage('bot', 'Desculpe, ocorreu um erro ao conectar com o servidor. Tente novamente mais tarde.');
        }
    });

    clearBtn.addEventListener('click', async () => {
        try {
            await fetch('/api/clear', { method: 'POST' });
            
            // Limpa a tela do chat mantendo apenas o indicador (que está oculto)
            const html = `
                <div class="message bot">
                    <div class="message-content">
                        Histórico limpo. Olá! Sou o assistente virtual da AgendaFlow. Como posso te ajudar hoje?
                    </div>
                    <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
            `;
            chatBox.innerHTML = html;
            chatBox.appendChild(typingIndicator);
            
        } catch (error) {
            console.error('Erro ao limpar conversa', error);
        }
    });

    function appendMessage(sender, text) {
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Formatar quebras de linha em <br> para HTML
        const formattedText = text.replace(/\n/g, '<br>');

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        messageDiv.innerHTML = `
            <div class="message-content">${formattedText}</div>
            <div class="message-time">${time}</div>
        `;
        
        // Insere a mensagem antes do indicador de digitação
        chatBox.insertBefore(messageDiv, typingIndicator);
        
        scrollToBottom();
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        scrollToBottom();
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
