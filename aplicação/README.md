# Sistema de Agendamento de Serviços

Aplicação para pequenos empreendedores gerenciarem agendamentos de serviços (ex: corte de cabelo, manicure, barba), com um painel administrativo em desktop e um chatbot simulando o atendimento via WhatsApp.

## Visão geral

O projeto é dividido em duas frentes que compartilham a mesma base de dados (`agendamentos.json`):

1. **Painel do empreendedor** (`main.py` + `interface.py`): uma aplicação desktop (Tkinter) onde o dono do negócio visualiza, cadastra, edita, exclui e conclui agendamentos.
2. **Chatbot do cliente** (`chatbot.py`): uma simulação de atendimento via WhatsApp, onde o cliente conversa com um assistente virtual (IA) para marcar um horário.

Ambos os módulos usam o `gerenciador.py` como camada central de dados, garantindo que um agendamento feito pelo chatbot apareça automaticamente no painel do empreendedor (e vice-versa).

## Estrutura dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Lógica de negócio do painel administrativo (CRUD de agendamentos, filtros, atualização automática da tela). |
| `interface.py` | Construção visual da interface Tkinter (formulário, tabela, estilos, cores). |
| `gerenciador.py` | Camada de acesso a dados: criar, atualizar, excluir, verificar disponibilidade e listar horários ocupados, tudo persistido em `agendamentos.json`. |
| `chatbot.py` | Serviço de chatbot (via API da Groq) que conversa com o cliente, verifica disponibilidade e cria agendamentos usando *function calling*. |
| `agendamentos.json` | Arquivo de dados (gerado automaticamente) que armazena os agendamentos. |

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

## Como executar

### Painel do empreendedor
```bash
python main.py
```

### Chatbot (simulação via terminal)
```bash
python chatbot.py
```

## Requisitos

- Python 3.10+
- Dependências: `groq` (para o chatbot). `tkinter` já vem incluso na instalação padrão do Python na maioria dos sistemas.

```bash
pip install groq
```

## Observação importante de segurança

O arquivo `chatbot.py` atualmente contém uma chave de API da Groq **exposta diretamente no código**. Isso é um risco de segurança sério — qualquer pessoa com acesso ao código (ou a este repositório, se publicado) pode usar essa chave em seu nome. Recomenda-se:

1. Revogar essa chave imediatamente no painel da Groq e gerar uma nova.
2. Remover a chave do código e carregá-la a partir de uma variável de ambiente ou arquivo `.env` (não versionado), por exemplo:
   ```python
   api_key = os.environ.get("GROQ_API_KEY")
   ```
3. Adicionar `.env` ao `.gitignore` caso o projeto seja versionado com Git.

## Limitações atuais

- Persistência simples em arquivo JSON (sem banco de dados relacional).
- Sem autenticação/controle de acesso no painel administrativo.
- O chatbot roda como simulação de terminal, sem integração real com a API do WhatsApp.
