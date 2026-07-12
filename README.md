# 📅 AgendaFlow - Sistema de Agendamento Inteligente

Aplicação completa para pequenos empreendedores gerenciarem agendamentos de serviços (ex: corte de cabelo, manicure, barba). O AgendaFlow conta com um painel administrativo em Desktop (Tkinter) e um Chatbot Web (Flask) alimentado por Inteligência Artificial (Groq/Llama) para realizar o atendimento dos seus clientes de forma autônoma.

## 🚀 Funcionalidades Principais

### 1. Painel do Empreendedor (Desktop - `main.py`)
Interface administrativa desenvolvida em Tkinter para gerenciar o negócio:
- **Listagem Dinâmica:** Tabela com todos os agendamentos realizados, com atualização automática a cada 2 segundos (caso um cliente faça um novo agendamento via bot, ele aparece sozinho na tela).
- **Gestão de Agendamentos:** Permite criar novos agendamentos manualmente, editar, excluir ou marcar um agendamento como "Concluído" com um único clique.
- **Filtros e Busca:** Busca instantânea por nome do cliente ou tipo de serviço.
- **Exportação de Relatórios [NOVO]:** Botão para exportar os dados da tabela em formato `.csv` (com suporte a codificação `UTF-8 BOM` e separador `;`), feito para abrir perfeitamente no Excel sem erros de acentuação ou colunas desconfiguradas.

### 2. Interface Web para o Cliente (Chatbot - `app.py`)
Uma interface rica rodando no navegador para que os clientes agendem seus serviços:
- **Aplicação Web Moderna (Flask):** UI com design atraente, paleta de cores equilibrada, indicador de digitação ("digitando...") e suporte a balões de chat interativos em tempo real.
- **Integração IA (LLM via Groq):** O bot (`chatbot.py`) simula uma conversa humana de verdade. Ele sabe extrair o nome, serviço e data/hora.
- **Function Calling:** A Inteligência Artificial utiliza ferramentas de código para:
  - `verificar_disponibilidade`: checa se o horário está livre antes de permitir a marcação.
  - `obter_horarios_ocupados`: sugere de forma proativa horários livres caso a data solicitada já esteja ocupada.
  - `criar_agendamento`: salva tudo no sistema de forma transparente.
- **Compreensão Contextual:** O bot consegue entender expressões de tempo como "hoje", "amanhã de manhã" ou "quinta-feira que vem" sem que o usuário precise digitar a data exata.
- **Configuração Segura [NOVO]:** As chaves de acesso da Groq agora são lidas de forma segura através de variáveis de ambiente gerenciadas pelo arquivo `.env`.

## ⚙️ Como Instalar e Rodar

### Pré-requisitos
- Python 3.10 ou superior.
- Instalar as dependências do projeto executando:
  ```bash
  pip install flask python-dotenv groq
  ```

### Configurando a API
1. Na pasta `aplicação`, crie um arquivo chamado `.env` (se ainda não existir).
2. Adicione a sua chave da Groq neste formato:
   ```env
   GROQ_API_KEY=gsk_sua_chave_aqui...
   ```

### Iniciando a Aplicação
O sistema roda em duas partes independentes. Você pode abrir dois terminais dentro da pasta `aplicação`:

**Para o Painel Administrativo:**
```bash
python main.py
```

**Para a Interface Web do Chatbot (Clientes):**
```bash
python app.py
```
*(Acesse no navegador: `http://localhost:5000`)*

## 🧱 Arquitetura e Limitações
- **Persistência:** Os dados são guardados de forma simples no arquivo `agendamentos.json` localizado na raiz do projeto (como um banco de dados leve).
- **Sem Autenticação Administrativa:** O painel desktop assume uso em computador pessoal e não possui tela de login no momento.
