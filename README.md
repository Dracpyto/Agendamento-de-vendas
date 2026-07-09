#  AgendaFlow Sistema de Agendamento de Serviços

Aplicação para pequenos empreendedores gerenciarem agendamentos de serviços (ex: corte de cabelo, manicure, barba), com um painel administrativo em desktop e um chatbot simulando o atendimento via WhatsApp.

## Como funciona

### Painel do empreendedor (`main.py`)
- Lista todos os agendamentos em uma tabela, com busca por cliente ou serviço.
- Permite criar, editar, excluir e marcar um agendamento como "Concluído".
- Verifica periodicamente (a cada 2 segundos) se o arquivo de dados foi alterado externamente (por exemplo, por um agendamento feito via chatbot) e atualiza a tela automaticamente.

### Chatbot do cliente (`chatbot.py`)
- Simula uma conversa de WhatsApp em que o cliente informa nome, serviço desejado e data/hora.
- Usa um modelo de linguagem (Llama, via API da Groq) com *function calling* para:
  - `verificar_disponibilidade`: checar se o horário está livre antes de agendar.
  - `obter_horarios_ocupados`: sugerir horários alternativos quando o solicitado está ocupado.
  - `criar_agendamento`: efetivar o agendamento quando todas as informações estiverem completas.
- Interpreta expressões relativas de tempo (como "amanhã", "terça-feira que vem") com base na data/hora atual.

## Limitações atuais

- Persistência simples em arquivo JSON (sem banco de dados relacional).
- Sem autenticação/controle de acesso no painel administrativo.
- O chatbot roda como simulação de terminal, sem integração real com a API do WhatsApp.
