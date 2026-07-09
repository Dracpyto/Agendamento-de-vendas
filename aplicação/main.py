import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import gerenciador
from interface import InterfaceAgendamento


class AplicativoAgendamento(InterfaceAgendamento):
    """Classe responsável pela lógica de negócio da aplicação de agendamentos."""

    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Flow")
        self.root.geometry("1000x650")
        self.root.minsize(900, 550)

        # ID do agendamento atualmente selecionado para edição (None se for novo)
        self.id_agendamento_selecionado = None
        self.ultimo_mtime = None

        self.configurar_estilos()
        self.criar_componentes()
        self.carregar_dados()
        self.verificar_atualizacoes()



    def carregar_dados(self, texto_filtro=""):
        """Carrega os dados da fonte JSON e preenche a tabela."""
        # Atualiza o timestamp da última leitura
        try:
            from gerenciador import ARQUIVO_DB
            if os.path.exists(ARQUIVO_DB):
                self.ultimo_mtime = os.path.getmtime(ARQUIVO_DB)
        except Exception:
            pass

        # Limpar tabela atual
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        agendamentos = gerenciador.carregar_agendamentos()
        texto_filtro = texto_filtro.lower().strip()

        for agendamento in agendamentos:
            # Se houver filtro, checa se combina com cliente ou serviço
            if texto_filtro:
                combina_cliente = texto_filtro in agendamento["cliente"].lower()
                combina_servico = texto_filtro in agendamento["servico"].lower()
                if not (combina_cliente or combina_servico):
                    continue

            # Insere o agendamento na tabela
            self.tabela.insert("", "end", values=(
                agendamento["id"],
                agendamento["cliente"],
                agendamento["servico"],
                agendamento["data_hora"],
                agendamento["status"],
                agendamento["observacoes"]
            ))

    def verificar_atualizacoes(self):
        """Verifica periodicamente se o arquivo de agendamentos foi modificado."""
        try:
            from gerenciador import ARQUIVO_DB
            if os.path.exists(ARQUIVO_DB):
                mtime = os.path.getmtime(ARQUIVO_DB)
                if self.ultimo_mtime is None:
                    self.ultimo_mtime = mtime
                elif mtime > self.ultimo_mtime:
                    self.ultimo_mtime = mtime
                    self.carregar_dados(self.var_busca.get())
        except Exception:
            pass
        self.root.after(2000, self.verificar_atualizacoes)

    def filtrar_dados(self, *args):
        """Callback acionado ao digitar na caixa de pesquisa."""
        busca = self.var_busca.get()
        self.carregar_dados(busca)

    def limpar_formulario(self):
        """Limpa todos os campos de texto do formulário."""
        self.id_agendamento_selecionado = None
        self.var_titulo_formulario.set("Novo Agendamento")

        self.entrada_cliente.delete(0, tk.END)
        self.entrada_servico.delete(0, tk.END)
        self.entrada_data_hora.delete(0, tk.END)
        self.entrada_data_hora.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.cb_status.set("Pendente")
        self.texto_observacoes.delete("1.0", tk.END)

        # Desmarcar seleções na tabela
        for item_selecionado in self.tabela.selection():
            self.tabela.selection_remove(item_selecionado)

    def salvar_agendamento(self):
        """Lida com a criação de novos agendamentos ou atualização dos existentes."""
        cliente = self.entrada_cliente.get().strip()
        servico = self.entrada_servico.get().strip()
        data_hora = self.entrada_data_hora.get().strip()
        status = self.cb_status.get()
        observacoes = self.texto_observacoes.get("1.0", tk.END).strip()

        # Validação básica
        if not cliente or not servico or not data_hora:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha os campos Cliente, Serviço e Data/Hora.")
            return

        if self.id_agendamento_selecionado is None:
            # Operação de Criar (Create)
            novo = gerenciador.criar_agendamento(cliente, servico, data_hora, status, observacoes)
            if novo:
                messagebox.showinfo("Sucesso", f"Agendamento para {cliente} cadastrado com sucesso!")
                self.limpar_formulario()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao salvar o agendamento no arquivo JSON.")
        else:
            # Operação de Atualizar (Update)
            sucesso = gerenciador.atualizar_agendamento(self.id_agendamento_selecionado, cliente, servico, data_hora, status, observacoes)
            if sucesso:
                messagebox.showinfo("Sucesso", "Agendamento atualizado com sucesso!")
                self.limpar_formulario()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar o agendamento.")

    def editar_selecionado(self):
        """Carrega o item selecionado na tabela de volta para o formulário de edição."""
        itens_selecionados = self.tabela.selection()
        if not itens_selecionados:
            messagebox.showwarning("Seleção Requerida", "Selecione um agendamento na lista para editar.")
            return

        # Pega os valores da primeira linha selecionada
        item = itens_selecionados[0]
        valores = self.tabela.item(item, "values")

        self.id_agendamento_selecionado = valores[0]
        self.var_titulo_formulario.set(f"Editar Agendamento (ID: {self.id_agendamento_selecionado})")

        # Preencher o formulário
        self.entrada_cliente.delete(0, tk.END)
        self.entrada_cliente.insert(0, valores[1])

        self.entrada_servico.delete(0, tk.END)
        self.entrada_servico.insert(0, valores[2])

        self.entrada_data_hora.delete(0, tk.END)
        self.entrada_data_hora.insert(0, valores[3])

        self.cb_status.set(valores[4])

        self.texto_observacoes.delete("1.0", tk.END)
        self.texto_observacoes.insert("1.0", valores[5])

    def excluir_selecionado(self):
        """Exclui o agendamento selecionado da tabela e do arquivo JSON."""
        itens_selecionados = self.tabela.selection()
        if not itens_selecionados:
            messagebox.showwarning("Seleção Requerida", "Selecione um agendamento na lista para excluir.")
            return

        item = itens_selecionados[0]
        valores = self.tabela.item(item, "values")
        id_agendamento = valores[0]
        nome_cliente = valores[1]

        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o agendamento de '{nome_cliente}'?")
        if confirmar:
            sucesso = gerenciador.excluir_agendamento(id_agendamento)
            if sucesso:
                messagebox.showinfo("Sucesso", "Agendamento excluído com sucesso.")
                # Se o item excluído estava sendo editado, limpa o formulário
                if self.id_agendamento_selecionado == id_agendamento:
                    self.limpar_formulario()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o agendamento.")

    def concluir_selecionado(self):
        """Muda o status do agendamento selecionado diretamente para 'Concluído'."""
        itens_selecionados = self.tabela.selection()
        if not itens_selecionados:
            messagebox.showwarning("Seleção Requerida", "Selecione um agendamento na lista para concluir.")
            return

        item = itens_selecionados[0]
        valores = self.tabela.item(item, "values")
        id_agendamento = valores[0]

        sucesso = gerenciador.atualizar_agendamento(id_agendamento, status="Concluído")
        if sucesso:
            messagebox.showinfo("Sucesso", "Status do agendamento alterado para 'Concluído'!")
            if self.id_agendamento_selecionado == id_agendamento:
                self.cb_status.set("Concluído")
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", "Não foi possível atualizar o status do agendamento.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicativoAgendamento(root)
    root.mainloop()
