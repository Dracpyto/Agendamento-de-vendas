import os 
import json
from datetime import datetime
from groq import Groq
import gerenciador

os.environ["GROQ_API_KEY"] = "insira sua chave API"

class ChatbotService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def obter_prompt_sistema(self):
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y")
        hora_formatada = agora.strftime("%H:%M")
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        dia_semana = dias_semana[agora.weekday()]
        
        return (
            "Você é um assistente virtual de agendamentos inteligente e prestativo para uma empresa.\n"
            f"A data atual de hoje é {data_formatada} ({dia_semana}) e o horário atual é {hora_formatada}.\n\n"
            "Diretrizes:\n"
            "1. Seja simpático, acolhedor e profissional.\n"
            "2. Para fazer um agendamento, você precisa obter do cliente:\n"
            "   - O nome completo dele(a)\n"
            "   - O serviço desejado (ex: corte de cabelo, manicure, barba)\n"
            "   - A data e o horário desejados (no formato DD/MM/AAAA HH:MM)\n"
            "3. ANTES de criar o agendamento, você DEVE verificar se a data e hora estão disponíveis usando a ferramenta `verificar_disponibilidade`.\n"
            "4. Se o horário estiver ocupado, informe amigavelmente que está indisponível e use a ferramenta `obter_horarios_ocupados` para o dia solicitado, listando as horas já ocupadas e sugerindo alternativas livres.\n"
            "5. Quando tiver todas as informações necessárias e o horário estiver vago, chame a ferramenta `criar_agendamento` para salvar o pedido.\n"
            "6. Interprete expressões relativas de tempo (como 'amanhã', 'hoje', 'terça-feira que vem') com base na data de hoje especificada acima e converta sempre para o formato DD/MM/AAAA HH:MM quando chamar as ferramentas.\n"
            "7. Mantenha as respostas concisas e guie o cliente de forma simples."
        )

    def obter_tools_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "verificar_disponibilidade",
                    "description": "Verifica se uma data e hora específica está disponível para agendamento. Use isso sempre antes de tentar agendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_hora": {
                                "type": "string",
                                "description": "A data e hora no formato DD/MM/AAAA HH:MM (ex: 15/07/2026 14:00)."
                            }
                        },
                        "required": ["data_hora"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "criar_agendamento",
                    "description": "Cria um novo agendamento de serviço após confirmar que o horário está disponível.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cliente": {
                                "type": "string",
                                "description": "Nome completo do cliente."
                            },
                            "servico": {
                                "type": "string",
                                "description": "Nome do serviço desejado."
                            },
                            "data_hora": {
                                "type": "string",
                                "description": "A data e hora do agendamento no formato DD/MM/AAAA HH:MM (ex: 15/07/2026 14:00)."
                            },
                            "observacoes": {
                                "type": "string",
                                "description": "Observações adicionais fornecidas pelo cliente (opcional)."
                            }
                        },
                        "required": ["cliente", "servico", "data_hora"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "obter_horarios_ocupados",
                    "description": "Lista as horas que já estão ocupadas em uma determinada data. Útil para sugerir alternativas ao cliente.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "string",
                                "description": "A data no formato DD/MM/AAAA (ex: 15/07/2026)."
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        ]

    def enviar_mensagem(self, historico_mensagens, texto_usuario):
        """
        Adiciona a mensagem do usuário ao histórico, processa chamadas de ferramentas
        se o modelo solicitar, e retorna a resposta final do assistente.
        """
        # Se for o início, podemos injetar a instrução do sistema atualizada
        if not historico_mensagens or historico_mensagens[0].get("role") != "system":
            historico_mensagens.insert(0, {"role": "system", "content": self.obter_prompt_sistema()})
        else:
            # Atualiza o prompt do sistema para ter a hora certa de cada turno
            historico_mensagens[0]["content"] = self.obter_prompt_sistema()

        historico_mensagens.append({"role": "user", "content": texto_usuario})

        while True:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=historico_mensagens,
                tools=self.obter_tools_schema(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1024
            )

            message = completion.choices[0].message
            
            # Se não houver chamadas de ferramentas, terminamos
            if not message.tool_calls:
                historico_mensagens.append({"role": "assistant", "content": message.content})
                return message.content

            # Adiciona a mensagem do assistente que contém a chamada de ferramenta ao histórico
            tool_calls_list = []
            for tc in message.tool_calls:
                tool_calls_list.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
            
            historico_mensagens.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": tool_calls_list
            })

            # Processa as chamadas de ferramentas
            for tc in message.tool_calls:
                fn_name = tc.function.name
                args = json.loads(tc.function.arguments)
                
                if fn_name == "verificar_disponibilidade":
                    dh = args.get("data_hora")
                    disponivel = gerenciador.verificar_disponibilidade(dh)
                    resultado = {"disponivel": disponivel}
                    
                elif fn_name == "criar_agendamento":
                    cli = args.get("cliente")
                    ser = args.get("servico")
                    dh = args.get("data_hora")
                    obs = args.get("observacoes", "")
                    
                    if not gerenciador.verificar_disponibilidade(dh):
                        resultado = {"sucesso": False, "erro": "Horário já ocupado por outro cliente."}
                    else:
                        novo = gerenciador.criar_agendamento(cli, ser, dh, observacoes=obs)
                        if novo:
                            resultado = {"sucesso": True, "agendamento": novo}
                        else:
                            resultado = {"sucesso": False, "erro": "Erro interno ao salvar no banco de dados."}
                            
                elif fn_name == "obter_horarios_ocupados":
                    dt = args.get("data")
                    ocupados = gerenciador.obter_horarios_ocupados(dt)
                    resultado = {"horarios_ocupados": ocupados}
                else:
                    resultado = {"erro": f"Ferramenta desconhecida: {fn_name}"}

                historico_mensagens.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": fn_name,
                    "content": json.dumps(resultado)
                })

if __name__ == "__main__":
    print("Bem-vindo ao Chatbot de Agendamentos. Digite 'sair' para encerrar.")
    chatbot = ChatbotService()
    historico = []
    
    # Primeira mensagem de saudação
    response = chatbot.enviar_mensagem(historico, "Olá! Sou cliente e quero informações.")
    print(f"\nChatbot: {response}")
    
    while True:
        try:
            user_input = input("\nVocê: ")
            if user_input.lower() == 'sair':
                break
            if not user_input.strip():
                continue
            response = chatbot.enviar_mensagem(historico, user_input)
            print(f"\nChatbot: {response}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nErro no processamento: {e}")