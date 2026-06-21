# ⚙️ Documentação dos Fluxos n8n — AgendAI

Este documento detalha a construção técnica de cada fluxo no n8n, incluindo configuração dos nodes, expressões e lógica de decisão.

---

## Fluxo 1: Atendimento e Agendamento (`01-atendimento-agendamento.json`)

### Objetivo
Receber mensagens do WhatsApp, interpretar com IA e criar agendamentos no Google Calendar e Supabase.

### Nodes e Configuração

#### Node 1 — `Webhook`
```
Type: Webhook
HTTP Method: POST
Path: /whatsapp-incoming
Response Mode: Respond Immediately
Authentication: Header Auth
  Header Name: x-webhook-token
  Header Value: {{ $env.WEBHOOK_SECRET }}
```

**Output esperado:**
```json
{
  "data": {
    "key": { "remoteJid": "5511999999999@s.whatsapp.net" },
    "message": { "conversation": "Quero agendar um horário" },
    "pushName": "João Silva"
  }
}
```

---

#### Node 2 — `Normalizar Mensagem` (Code Node)
```javascript
// Extrai dados relevantes da mensagem do WhatsApp
const body = $input.first().json;
const whatsapp = body.data.key.remoteJid.replace('@s.whatsapp.net', '');
const message = body.data.message?.conversation 
  || body.data.message?.extendedTextMessage?.text 
  || '';
const senderName = body.data.pushName || '';

return [{
  json: {
    whatsapp,
    message,
    senderName,
    timestamp: new Date().toISOString()
  }
}];
```

---

#### Node 3 — `Buscar Contexto` (Supabase)
```
Operation: Select
Table: conversations
Filters:
  - client_whatsapp = {{ $json.whatsapp }}
Limit: 1
```

---

#### Node 4 — `Buscar Horários Disponíveis` (Google Calendar)
```
Operation: Get Many Events
Calendar ID: {{ $env.GOOGLE_CALENDAR_ID }}
Time Min: {{ DateTime.now().toISO() }}
Time Max: {{ DateTime.now().plus({ days: 14 }).toISO() }}
```

> **Nota:** Um Code Node subsequente processa os eventos e calcula os slots livres com base em `working_hours` do tenant.

---

#### Node 5 — `IA Claude` (HTTP Request)
```
Method: POST
URL: https://api.anthropic.com/v1/messages
Headers:
  x-api-key: {{ $env.ANTHROPIC_API_KEY }}
  anthropic-version: 2023-06-01
  content-type: application/json

Body (JSON):
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 500,
  "system": "{{ $node['System Prompt'].json.prompt }}",
  "messages": [
    {
      "role": "user",
      "content": "{{ $json.message }}"
    }
  ]
}
```

**Parsear resposta (Code Node):**
```javascript
const response = $input.first().json;
const text = response.content[0].text;

// Tenta extrair JSON da resposta
let action = { type: 'chat', reply: text };
try {
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    action = JSON.parse(jsonMatch[0]);
  }
} catch(e) {}

return [{ json: { ...action, rawReply: text } }];
```

---

#### Node 6 — `Switch: Ação` 
```
Conditions:
  - Output 1: {{ $json.action === 'schedule' }}
  - Output 2: {{ $json.action === 'reschedule' }}
  - Output 3: {{ $json.action === 'cancel' }}
  - Output 4: {{ $json.action === 'query' }}
  - Output 5: true (default — resposta de chat)
```

---

#### Node 7 — `Salvar no Supabase` (caminho schedule)
```
Operation: Insert
Table: appointments
Data:
  tenant_id: {{ $env.TENANT_ID }}
  client_id: {{ $node['Buscar/Criar Cliente'].json.id }}
  service: {{ $json.service }}
  scheduled_at: {{ $json.datetime }}
  status: confirmed
  notes: {{ $json.notes }}
```

---

#### Node 8 — `Criar Evento Google Calendar`
```
Operation: Create Event
Calendar ID: {{ $env.GOOGLE_CALENDAR_ID }}
Title: Agendamento - {{ $json.client_name }} - {{ $json.service }}
Start: {{ $json.datetime }}
End: {{ DateTime.fromISO($json.datetime).plus({ minutes: 60 }).toISO() }}
Description: Cliente: {{ $json.client_name }}\nTel: {{ $json.whatsapp }}\nServiço: {{ $json.service }}
```

---

#### Node 9 — `Enviar Confirmação WA` (HTTP Request)
```
Method: POST
URL: {{ $env.EVOLUTION_API_URL }}/message/sendText/{{ $env.EVOLUTION_INSTANCE }}
Headers:
  apikey: {{ $env.EVOLUTION_API_KEY }}

Body:
{
  "number": "{{ $json.whatsapp }}",
  "text": "✅ *Agendamento Confirmado!*\n\n📅 Data: {{ $json.formattedDate }}\n⏰ Horário: {{ $json.formattedTime }}\n💼 Serviço: {{ $json.service }}\n\nEnvie *CANCELAR* a qualquer momento para cancelar."
}
```

---

## Fluxo 2: Lembretes Automáticos (`03-lembretes.json`)

### Node 1 — `Schedule Trigger`
```
Trigger At: Every Day
Hour: 8
Minute: 0
Timezone: America/Sao_Paulo
```

### Node 2 — `Buscar Agendamentos de Amanhã` (Supabase)
```sql
SELECT a.*, c.whatsapp, c.name as client_name
FROM appointments a
JOIN clients c ON c.id = a.client_id
WHERE 
  a.status = 'confirmed'
  AND a.reminder_sent = false
  AND DATE(a.scheduled_at) = CURRENT_DATE + INTERVAL '1 day'
```

### Node 3 — `Loop: Para Cada Agendamento` (Split In Batches)
```
Batch Size: 1
```

### Node 4 — `Enviar Lembrete`
```
Mensagem:
⏰ *Lembrete de Agendamento*

Olá, {{ $json.client_name }}! 
Seu agendamento é *amanhã*:

📅 {{ $json.formatted_date }}
⏰ {{ $json.formatted_time }}
💼 {{ $json.service }}

Responda *CONFIRMAR* ou *CANCELAR*.
```

### Node 5 — `Marcar Lembrete Enviado` (Supabase Update)
```
Table: appointments
Data: { reminder_sent: true }
Filter: id = {{ $json.id }}
```

---

## Fluxo 3: Reagendamento (`02-reagendamento.json`)

O fluxo de reagendamento é um sub-fluxo chamado pelo Fluxo 1 via `Execute Workflow` node quando `action === 'reschedule'`.

```
[Buscar agendamento atual no Supabase]
  → [Calcular próximos 5 slots disponíveis]
  → [Enviar opções numeradas via WA]
  → [Atualizar estado da conversa para 'awaiting_reschedule']
  → [Webhook recebe resposta com número escolhido]
  → [Atualizar appointment no Supabase]
  → [Atualizar evento no Google Calendar]
  → [Confirmar novo horário via WA]
```

### Mensagem de Opções
```
🔄 *Reagendamento*

Seus próximos horários disponíveis:

1️⃣ Seg, 24/06 às 09:00
2️⃣ Seg, 24/06 às 14:00
3️⃣ Ter, 25/06 às 10:00
4️⃣ Qua, 26/06 às 09:00
5️⃣ Qua, 26/06 às 16:00

Responda com o número da opção desejada.
```

---

## Tratamento de Erros

Todos os fluxos incluem um node de erro global:

```
Type: Error Trigger
→ HTTP Request → Evolution API (notifica empreendedor)
→ Supabase Insert → errors_log table
```

### Tabela de erros
```sql
CREATE TABLE errors_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flow_name TEXT,
  error_message TEXT,
  payload JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```
