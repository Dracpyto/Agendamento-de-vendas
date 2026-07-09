import json
import os
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.abspath(os.path.join(BASE_DIR, "..", "agendamentos.json"))

def carregar_agendamentos():
    """Carrega os agendamentos do arquivo JSON."""
    if not os.path.exists(ARQUIVO_DB):
        return []
    try:
        with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def salvar_agendamentos(agendamentos):
    """Salva a lista de agendamentos no arquivo JSON."""
    try:
        with open(ARQUIVO_DB, "w", encoding="utf-8") as f:
            json.dump(agendamentos, f, ensure_ascii=False, indent=4)
        return True
    except IOError:
        return False

def criar_agendamento(cliente, servico, data_hora, status="Pendente", observacoes=""):
    """Cria um novo agendamento e salva no JSON."""
    agendamentos = carregar_agendamentos()
    
    novo_agendamento = {
        "id": str(uuid.uuid4())[:8],  # Gerar um ID curto de 8 caracteres
        "cliente": cliente.strip(),
        "servico": servico.strip(),
        "data_hora": data_hora.strip(),
        "status": status,
        "observacoes": observacoes.strip(),
        "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    agendamentos.append(novo_agendamento)
    if salvar_agendamentos(agendamentos):
        return novo_agendamento
    return None

def atualizar_agendamento(agendamento_id, cliente=None, servico=None, data_hora=None, status=None, observacoes=None):
    """Atualiza um agendamento existente pelo ID."""
    agendamentos = carregar_agendamentos()
    atualizado = False
    
    for agendamento in agendamentos:
        if agendamento["id"] == agendamento_id:
            if cliente is not None:
                agendamento["cliente"] = cliente.strip()
            if servico is not None:
                agendamento["servico"] = servico.strip()
            if data_hora is not None:
                agendamento["data_hora"] = data_hora.strip()
            if status is not None:
                agendamento["status"] = status
            if observacoes is not None:
                agendamento["observacoes"] = observacoes.strip()
            atualizado = True
            break
            
    if atualizado:
        salvar_agendamentos(agendamentos)
        return True
    return False

def excluir_agendamento(agendamento_id):
    """Exclui um agendamento existente pelo ID."""
    agendamentos = carregar_agendamentos()
    tamanho_inicial = len(agendamentos)
    
    # Filtrar removendo o agendamento correspondente
    agendamentos = [ag for ag in agendamentos if ag["id"] != agendamento_id]
    
    if len(agendamentos) < tamanho_inicial:
        salvar_agendamentos(agendamentos)
        return True
    return False

def verificar_disponibilidade(data_hora):
    """Verifica se já existe um agendamento para a data e hora informadas (que não esteja cancelado)."""
    agendamentos = carregar_agendamentos()
    data_hora_busca = data_hora.strip()
    for ag in agendamentos:
        if ag.get("status") != "Cancelado" and ag.get("data_hora", "").strip() == data_hora_busca:
            return False
    return True

def obter_horarios_ocupados(data):
    """Retorna a lista de horários ocupados para uma determinada data (DD/MM/AAAA)."""
    agendamentos = carregar_agendamentos()
    data_busca = data.strip()
    ocupados = []
    for ag in agendamentos:
        if ag.get("status") != "Cancelado":
            partes = ag.get("data_hora", "").strip().split(" ")
            if len(partes) >= 1 and partes[0] == data_busca:
                if len(partes) > 1:
                    ocupados.append(partes[1])
                else:
                    ocupados.append(ag.get("data_hora", "").strip())
    return ocupados

