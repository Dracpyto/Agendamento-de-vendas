import tkinter as tk
from tkinter import ttk
import threading
from chatbot import ChatbotService

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot de Agendamento")
        self.root.geometry("600x700")
        self.root.configure(bg="#f3f4f6")
        
        # Instancia o serviço de chatbot
        self.chatbot = ChatbotService()
        self.historico = []
        
        self.configurar_interface()
        self.iniciar_chat()

    def configurar_interface(self):
        # Frame principal
        frame_principal = tk.Frame(self.root, bg="#f3f4f6")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        lbl_titulo = tk.Label(frame_principal, text="🤖 Chat de Agendamento", font=("Segoe UI", 16, "bold"), bg="#f3f4f6", fg="#111827")
        lbl_titulo.pack(pady=(0, 10))
        
        # Área de chat
        frame_chat = tk.Frame(frame_principal, bg="#ffffff", bd=1, relief="solid")
        frame_chat.pack(fill="both", expand=True, pady=(0, 15))
        
        self.scrollbar = tk.Scrollbar(frame_chat)
        self.scrollbar.pack(side="right", fill="y")
        
        self.chat_display = tk.Text(frame_chat, wrap="word", font=("Segoe UI", 10), bg="#ffffff", yscrollcommand=self.scrollbar.set, state="disabled")
        self.chat_display.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.config(command=self.chat_display.yview)
        
        # Tags para colorir as mensagens
        self.chat_display.tag_config("user", foreground="#3b82f6", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("bot", foreground="#10b981", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("msg", foreground="#1f2937", font=("Segoe UI", 10))
        
        # Área de input
        frame_input = tk.Frame(frame_principal, bg="#f3f4f6")
        frame_input.pack(fill="x")
        
        self.entrada_msg = ttk.Entry(frame_input, font=("Segoe UI", 12))
        self.entrada_msg.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.entrada_msg.bind("<Return>", lambda event: self.enviar_mensagem())
        
        self.btn_enviar = ttk.Button(frame_input, text="Enviar", command=self.enviar_mensagem)
        self.btn_enviar.pack(side="right", ipady=3)
        
    def exibir_mensagem(self, remetente, mensagem, tag_remetente):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{remetente}: ", tag_remetente)
        self.chat_display.insert(tk.END, f"{mensagem}\n\n", "msg")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def iniciar_chat(self):
        # Desabilita entrada enquanto inicializa
        self.entrada_msg.config(state="disabled")
        self.btn_enviar.config(state="disabled")
        
        def run():
            try:
                response = self.chatbot.enviar_mensagem(self.historico, "Olá! Sou cliente e quero informações.")
                self.root.after(0, self.exibir_mensagem, "Chatbot", response, "bot")
            except Exception as e:
                self.root.after(0, self.exibir_mensagem, "Sistema", f"Erro de conexão com API: {e}\n\nVerifique se a API Key (GROQ_API_KEY) está configurada corretamente em chatbot.py.", "bot")
            finally:
                self.root.after(0, self.habilitar_input)
                
        threading.Thread(target=run, daemon=True).start()

    def habilitar_input(self):
        self.entrada_msg.config(state="normal")
        self.btn_enviar.config(state="normal")
        self.entrada_msg.focus()

    def enviar_mensagem(self):
        msg = self.entrada_msg.get().strip()
        if not msg:
            return
            
        self.entrada_msg.delete(0, tk.END)
        self.exibir_mensagem("Você", msg, "user")
        
        self.entrada_msg.config(state="disabled")
        self.btn_enviar.config(state="disabled")
        
        def run():
            try:
                response = self.chatbot.enviar_mensagem(self.historico, msg)
                self.root.after(0, self.exibir_mensagem, "Chatbot", response, "bot")
            except Exception as e:
                self.root.after(0, self.exibir_mensagem, "Sistema", f"Erro ao processar: {e}", "bot")
            finally:
                self.root.after(0, self.habilitar_input)

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configurar estilo dos botões ttk
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", background="#3b82f6", foreground="white", borderwidth=0, padding=6)
    style.map("TButton", background=[("active", "#2563eb")])
    
    app = ChatbotGUI(root)
    root.mainloop()
