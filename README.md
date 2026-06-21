# 📅 AgendAI — Plataforma de Agendamentos para Pequenos Empreendedores

> Automação inteligente de agendamentos via WhatsApp com IA, construída sobre **n8n**, com painel de controle exclusivo para MEIs.

---

## 🧭 Visão Geral

O **AgendAI** é uma solução SaaS de agendamento online voltada para microempreendedores individuais (MEIs) que desejam automatizar o atendimento e a gestão de compromissos sem precisar de conhecimento técnico avançado.

O sistema funciona com:
- 🤖 **Bot de WhatsApp com IA** para atender, agendar e reagendar automaticamente
- 📊 **Dashboard do Empreendedor** para visualizar e gerenciar todos os agendamentos
- ⚙️ **Fluxos n8n** que orquestram toda a lógica de negócio, integrações e automações

---

## 🏗️ Arquitetura da Solução

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENTE FINAL                         │
│                  (envia msg no WhatsApp)                     │
└─────────────────────────┬────────────────────────────────────┘
                          │ Webhook
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    EVOLUTION API / WPPConnect                │
│              (Gateway de WhatsApp Business)                  │
└─────────────────────────┬────────────────────────────────────┘
                          │ POST /webhook
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                         n8n Cloud                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Webhook    │→ │   IA Claude  │→ │  Google Calendar / │  │
│  │  Trigger    │  │  (Anthropic) │  │  Supabase DB       │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
│         │               │                      │             │
│         └───────────────▼──────────────────────┘            │
│                  ┌──────────────┐                            │
│                  │ Resposta WA  │                            │
│                  └──────────────┘                            │
└──────────────────────────────────────────────────────────────┘
                          │ API REST
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                DASHBOARD DO EMPREENDEDOR (MEI)               │
│              (React SPA hospedada em Vercel/Netlify)         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 Stack Tecnológica

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| Automação | **n8n** (Cloud ou Self-hosted) | Orquestração de fluxos |
| Bot WhatsApp | **Evolution API** ou **WPPConnect** | Gateway de mensagens |
| IA | **Claude (Anthropic)** via HTTP | Interpretação e resposta |
| Banco de Dados | **Supabase** (PostgreSQL) | Armazenamento de dados |
| Calendário | **Google Calendar API** | Gestão de disponibilidade |
| Notificações | **WhatsApp + E-mail (SMTP)** | Confirmações e lembretes |
| Dashboard | **React + Tailwind + Vite** | Interface do MEI |
| Hospedagem | **Vercel** (Dashboard) + **VPS/Railway** (n8n) | Infraestrutura |

---

## 🔄 Fluxos n8n — Detalhamento

### Fluxo 1: Atendimento e Agendamento

```
[Webhook WA] → [Switch: Intenção] → [IA: Extrair dados]
     → [Checar disponibilidade no Calendar]
     → [Criar evento no Calendar + registro no Supabase]
     → [Enviar confirmação via WA]
     → [Agendar lembrete 24h antes]
```

**Nodes utilizados:**
1. `Webhook` — recebe mensagem do WA
2. `Switch` — classifica intenção: agendar / reagendar / cancelar / consultar
3. `HTTP Request` → Anthropic Claude — processa linguagem natural
4. `Google Calendar` — verifica slots disponíveis
5. `Supabase` — salva agendamento
6. `HTTP Request` → Evolution API — envia resposta ao cliente
7. `Schedule Trigger` — dispara lembrete 24h antes

---

### Fluxo 2: Reagendamento Automático

```
[Webhook WA] → [IA: Detecta pedido de reagendamento]
     → [Buscar agendamento no Supabase]
     → [Listar horários disponíveis]
     → [Apresentar opções ao cliente via WA]
     → [Aguardar resposta] → [Confirmar novo horário]
     → [Atualizar Calendar + Supabase]
     → [Notificar empreendedor no Dashboard]
```

---

### Fluxo 3: Lembrete Automático

```
[Schedule Trigger: todo dia 08h]
     → [Buscar agendamentos de amanhã no Supabase]
     → [Loop: Para cada agendamento]
          → [Enviar lembrete personalizado via WA]
          → [Registrar envio no Supabase]
```

---

### Fluxo 4: Cancelamento

```
[Webhook WA] → [IA: Detecta cancelamento]
     → [Buscar agendamento] → [Atualizar status no Supabase]
     → [Deletar evento no Google Calendar]
     → [Notificar empreendedor]
     → [Enviar confirmação de cancelamento ao cliente]
```

---

## 🗄️ Estrutura do Banco de Dados (Supabase)

### Tabela: `tenants` (Empreendedores)
```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  whatsapp TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  business_name TEXT,
  business_type TEXT,
  working_hours JSONB DEFAULT '{"seg":["08:00","18:00"],"ter":["08:00","18:00"]}',
  slot_duration INT DEFAULT 60, -- minutos por atendimento
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `clients`
```sql
CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  name TEXT,
  whatsapp TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `appointments`
```sql
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  client_id UUID REFERENCES clients(id),
  service TEXT,
  scheduled_at TIMESTAMP NOT NULL,
  duration INT DEFAULT 60,
  status TEXT DEFAULT 'confirmed', -- confirmed | cancelled | rescheduled | completed
  notes TEXT,
  google_event_id TEXT,
  reminder_sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `conversations`
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  client_whatsapp TEXT NOT NULL,
  state TEXT DEFAULT 'idle', -- idle | collecting_name | collecting_service | collecting_date | confirming
  context JSONB DEFAULT '{}',
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🤖 Prompt de IA (Claude)

O nó de IA no n8n utiliza o seguinte system prompt:

```
Você é um assistente de agendamentos para {business_name}, 
um(a) {business_type}. Seu nome é "Agen".

Suas responsabilidades:
1. Recepcionar clientes de forma cordial e profissional
2. Identificar a intenção: AGENDAR, REAGENDAR, CANCELAR ou CONSULTAR
3. Coletar: nome do cliente, serviço desejado, data e horário preferidos
4. Confirmar disponibilidade (você receberá os horários livres)
5. Confirmar o agendamento de forma clara

Regras:
- Responda SEMPRE em português brasileiro
- Seja breve e direto, máximo 3 linhas por mensagem
- Se a data/hora não estiver disponível, ofereça a próxima disponível
- Nunca confirme sem verificar disponibilidade
- Ao finalizar, retorne um JSON estruturado com: 
  { "action": "schedule|reschedule|cancel|query", "client_name": "", "service": "", "datetime": "ISO8601", "notes": "" }

Horários disponíveis: {available_slots}
Histórico: {conversation_history}
Mensagem atual: {user_message}
```

---

## 🚀 Como Executar (Setup)

### Pré-requisitos
- Conta no [n8n Cloud](https://n8n.io) ou instância self-hosted
- Conta no [Supabase](https://supabase.com)
- Conta no [Evolution API](https://evolution-api.com) ou WPPConnect
- API Key da [Anthropic](https://console.anthropic.com)
- Projeto no [Google Cloud Console](https://console.cloud.google.com) com Calendar API ativada

### 1. Configurar Supabase
```bash
# Clone este repositório
git clone https://github.com/seu-usuario/agendai.git
cd agendai

# Execute os scripts SQL na ordem
# Supabase Dashboard > SQL Editor
cat database/01_schema.sql | # cole no Supabase SQL Editor
cat database/02_rls.sql    | # políticas de segurança
cat database/03_seed.sql   | # dados iniciais
```

### 2. Importar Fluxos no n8n
```
n8n Dashboard → Workflows → Import from File
→ Importe cada arquivo de /n8n-flows/
```

### 3. Configurar Credenciais no n8n
| Credencial | Onde obter |
|-----------|-----------|
| `Anthropic API` | console.anthropic.com → API Keys |
| `Supabase` | Supabase → Settings → API |
| `Google Calendar OAuth2` | console.cloud.google.com |
| `Evolution API` | Painel da Evolution API |

### 4. Configurar Variáveis de Ambiente
```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
EVOLUTION_API_URL=https://sua-evolution.api
EVOLUTION_API_KEY=sua-chave
GOOGLE_CALENDAR_ID=seu-email@gmail.com
N8N_WEBHOOK_URL=https://seu-n8n.app.n8n.cloud/webhook/
```

### 5. Deploy do Dashboard
```bash
cd dashboard
npm install
npm run build

# Deploy para Vercel
npx vercel --prod

# Configure as variáveis de ambiente no Vercel:
# VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_N8N_WEBHOOK_URL
```

---

## 📁 Estrutura do Repositório

```
agendai/
├── README.md
├── n8n-flows/
│   ├── 01-atendimento-agendamento.json
│   ├── 02-reagendamento.json
│   ├── 03-lembretes.json
│   └── 04-cancelamento.json
├── database/
│   ├── 01_schema.sql
│   ├── 02_rls.sql
│   └── 03_seed.sql
├── dashboard/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── SETUP.md
│   ├── FLOWS.md
│   ├── API.md
│   └── images/
└── .env.example
```

---

## 🔐 Segurança

- Row Level Security (RLS) ativado no Supabase — cada tenant só vê seus dados
- Autenticação via Supabase Auth (magic link ou senha)
- Webhook URLs com token secreto para evitar chamadas externas
- Variáveis sensíveis nunca commited — use `.env.example`

---

## 🗺️ Roadmap

- [x] MVP: Agendamento, confirmação, lembrete, cancelamento
- [x] Dashboard básico do MEI
- [ ] Pagamento online integrado (Stripe / Mercado Pago)
- [ ] Multi-serviço com preços
- [ ] Relatórios e analytics
- [ ] App mobile (React Native)
- [ ] Integração com Instagram DM

---

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

---

## 🤝 Contribuição

PRs são bem-vindos! Leia [CONTRIBUTING.md](docs/CONTRIBUTING.md) antes de abrir issues ou pull requests.

---

> Feito com ❤️ para os microempreendedores brasileiros.
