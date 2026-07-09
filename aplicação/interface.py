import tkinter as tk
from tkinter import ttk
from datetime import datetime


class InterfaceAgendamento:
    """Classe responsável exclusivamente pela interface visual da aplicação."""

    def configurar_estilos(self):
        """Define o esquema de cores e estilos usando ttk."""
        self.root.configure(bg="#f3f4f6")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Cores
        self.cor_fundo = "#f3f4f6"
        self.cor_cartao = "#ffffff"
        self.cor_primaria = "#3b82f6"       # Azul
        self.cor_primaria_hover = "#2563eb"
        self.cor_sucesso = "#10b981"        # Verde
        self.cor_sucesso_hover = "#059669"
        self.cor_perigo = "#ef4444"         # Vermelho
        self.cor_perigo_hover = "#dc2626"
        self.cor_texto = "#1f2937"
        self.cor_texto_claro = "#4b5563"
        self.cor_borda = "#d1d5db"

        # Fontes
        self.fonte_titulo = ("Segoe UI", 16, "bold")
        self.fonte_subtitulo = ("Segoe UI", 12, "bold")
        self.fonte_rotulo = ("Segoe UI", 10, "bold")
        self.fonte_corpo = ("Segoe UI", 10)

        # Configuração de Estilos ttk
        self.style.configure(".", font=self.fonte_corpo, background=self.cor_fundo, foreground=self.cor_texto)

        # Botões
        self.style.configure("Primary.TButton", background=self.cor_primaria, foreground="white", borderwidth=0, padding=8)
        self.style.map("Primary.TButton", background=[("active", self.cor_primaria_hover)])

        self.style.configure("Success.TButton", background=self.cor_sucesso, foreground="white", borderwidth=0, padding=8)
        self.style.map("Success.TButton", background=[("active", self.cor_sucesso_hover)])

        self.style.configure("Danger.TButton", background=self.cor_perigo, foreground="white", borderwidth=0, padding=8)
        self.style.map("Danger.TButton", background=[("active", self.cor_perigo_hover)])

        self.style.configure("Secondary.TButton", background="#6b7280", foreground="white", borderwidth=0, padding=8)
        self.style.map("Secondary.TButton", background=[("active", "#4b5563")])

        # Tabela (Treeview)
        self.style.configure("Treeview",
                             background=self.cor_cartao,
                             foreground=self.cor_texto,
                             rowheight=30,
                             fieldbackground=self.cor_cartao,
                             borderwidth=0)
        self.style.configure("Treeview.Heading",
                             background="#e5e7eb",
                             foreground=self.cor_texto,
                             font=self.fonte_rotulo,
                             relief="flat",
                             padding=5)
        self.style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e40af")])

    def criar_componentes(self):
        """Constrói todos os widgets visuais da janela principal."""
        # Frame Principal com espaçamento periférico
        frame_principal = tk.Frame(self.root, bg=self.cor_fundo)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # TÍTULO DA APLICAÇÃO
        rotulo_titulo = tk.Label(frame_principal, text="📅 AgendaFlow", font=self.fonte_titulo, bg=self.cor_fundo, fg="#111827", anchor="w")
        rotulo_titulo.pack(fill="x", pady=(0, 15))

        # Conteúdo dividido em duas colunas (Esquerda: Formulário | Direita: Lista)
        frame_conteudo = tk.Frame(frame_principal, bg=self.cor_fundo)
        frame_conteudo.pack(fill="both", expand=True)
        frame_conteudo.columnconfigure(0, weight=1)  # Esquerda (Formulário)
        frame_conteudo.columnconfigure(1, weight=2)  # Direita (Tabela)
        frame_conteudo.rowconfigure(0, weight=1)

        # =====================================================================
        # COLUNA ESQUERDA: FORMULÁRIO DE CADASTRO / EDIÇÃO
        # =====================================================================
        container_formulario = tk.Frame(frame_conteudo, bg=self.cor_cartao, bd=1, relief="solid", highlightthickness=0)
        container_formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        formulario_interno = tk.Frame(container_formulario, bg=self.cor_cartao)
        formulario_interno.pack(fill="both", expand=True, padx=20, pady=20)

        self.var_titulo_formulario = tk.StringVar(value="Novo Agendamento")
        titulo_formulario = tk.Label(formulario_interno, textvariable=self.var_titulo_formulario, font=self.fonte_subtitulo, bg=self.cor_cartao, fg=self.cor_primaria, anchor="w")
        titulo_formulario.pack(fill="x", pady=(0, 15))

        # Campo: Cliente
        tk.Label(formulario_interno, text="Nome do Cliente:", font=self.fonte_rotulo, bg=self.cor_cartao, fg=self.cor_texto_claro, anchor="w").pack(fill="x", pady=(5, 2))
        self.entrada_cliente = ttk.Entry(formulario_interno, font=self.fonte_corpo)
        self.entrada_cliente.pack(fill="x", pady=(0, 10))

        # Campo: Serviço
        tk.Label(formulario_interno, text="Serviço:", font=self.fonte_rotulo, bg=self.cor_cartao, fg=self.cor_texto_claro, anchor="w").pack(fill="x", pady=(5, 2))
        self.entrada_servico = ttk.Entry(formulario_interno, font=self.fonte_corpo)
        self.entrada_servico.pack(fill="x", pady=(0, 10))

        # Campo: Data e Hora
        tk.Label(formulario_interno, text="Data e Hora (DD/MM/AAAA HH:MM):", font=self.fonte_rotulo, bg=self.cor_cartao, fg=self.cor_texto_claro, anchor="w").pack(fill="x", pady=(5, 2))
        self.entrada_data_hora = ttk.Entry(formulario_interno, font=self.fonte_corpo)
        self.entrada_data_hora.pack(fill="x", pady=(0, 10))
        self.entrada_data_hora.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))

        # Campo: Status
        tk.Label(formulario_interno, text="Status:", font=self.fonte_rotulo, bg=self.cor_cartao, fg=self.cor_texto_claro, anchor="w").pack(fill="x", pady=(5, 2))
        self.cb_status = ttk.Combobox(formulario_interno, values=["Pendente", "Confirmado", "Concluído", "Cancelado"], font=self.fonte_corpo, state="readonly")
        self.cb_status.set("Pendente")
        self.cb_status.pack(fill="x", pady=(0, 10))

        # Campo: Observações
        tk.Label(formulario_interno, text="Observações:", font=self.fonte_rotulo, bg=self.cor_cartao, fg=self.cor_texto_claro, anchor="w").pack(fill="x", pady=(5, 2))
        self.texto_observacoes = tk.Text(formulario_interno, font=self.fonte_corpo, height=4, wrap="word", bd=1, relief="solid", highlightthickness=0)
        self.texto_observacoes.pack(fill="both", expand=True, pady=(0, 15))

        # Botões de Ação do Formulário
        frame_botoes_formulario = tk.Frame(formulario_interno, bg=self.cor_cartao)
        frame_botoes_formulario.pack(fill="x")

        self.btn_salvar = ttk.Button(frame_botoes_formulario, text="Salvar", style="Success.TButton", command=self.salvar_agendamento)
        self.btn_salvar.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_limpar = ttk.Button(frame_botoes_formulario, text="Limpar", style="Secondary.TButton", command=self.limpar_formulario)
        self.btn_limpar.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # =====================================================================
        # COLUNA DIREITA: TABELA DE AGENDAMENTOS E FILTROS
        # =====================================================================
        container_direito = tk.Frame(frame_conteudo, bg=self.cor_fundo)
        container_direito.grid(row=0, column=1, sticky="nsew")

        # Filtro de Busca
        frame_busca = tk.Frame(container_direito, bg=self.cor_fundo)
        frame_busca.pack(fill="x", pady=(0, 10))

        tk.Label(frame_busca, text="🔍 Buscar por Cliente/Serviço:", font=self.fonte_rotulo, bg=self.cor_fundo, fg=self.cor_texto_claro).pack(side="left", padx=(0, 5))

        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", self.filtrar_dados)
        self.entrada_busca = ttk.Entry(frame_busca, textvariable=self.var_busca, font=self.fonte_corpo)
        self.entrada_busca.pack(side="left", fill="x", expand=True)

        # Tabela (Treeview) para listagem
        container_tabela = tk.Frame(container_direito, bg=self.cor_cartao, bd=1, relief="solid")
        container_tabela.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container_tabela, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        colunas = ("id", "cliente", "servico", "data_hora", "status", "observacoes")
        self.tabela = ttk.Treeview(container_tabela, columns=colunas, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tabela.yview)

        self.tabela.heading("id", text="ID")
        self.tabela.heading("cliente", text="Cliente")
        self.tabela.heading("servico", text="Serviço")
        self.tabela.heading("data_hora", text="Data e Hora")
        self.tabela.heading("status", text="Status")
        self.tabela.heading("observacoes", text="Observações")

        self.tabela.column("id", width=60, minwidth=50, anchor="center")
        self.tabela.column("cliente", width=150, minwidth=100)
        self.tabela.column("servico", width=120, minwidth=100)
        self.tabela.column("data_hora", width=120, minwidth=100, anchor="center")
        self.tabela.column("status", width=90, minwidth=80, anchor="center")
        self.tabela.column("observacoes", width=180, minwidth=120)

        self.tabela.pack(fill="both", expand=True)

        # Botões de Ação na Tabela
        frame_botoes_tabela = tk.Frame(container_direito, bg=self.cor_fundo)
        frame_botoes_tabela.pack(fill="x", pady=(15, 0))

        self.btn_editar = ttk.Button(frame_botoes_tabela, text="📝 Editar Selecionado", style="Primary.TButton", command=self.editar_selecionado)
        self.btn_editar.pack(side="left", padx=(0, 5), fill="x", expand=True)

        self.btn_excluir = ttk.Button(frame_botoes_tabela, text="🗑️ Excluir Selecionado", style="Danger.TButton", command=self.excluir_selecionado)
        self.btn_excluir.pack(side="left", padx=5, fill="x", expand=True)

        self.btn_concluir = ttk.Button(frame_botoes_tabela, text="✅ Concluir Agendamento", style="Success.TButton", command=self.concluir_selecionado)
        self.btn_concluir.pack(side="left", padx=(5, 0), fill="x", expand=True)
