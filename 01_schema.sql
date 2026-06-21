-- AgendAI — Schema completo do banco de dados
-- Execute no Supabase SQL Editor na ordem: 01 → 02 → 03

-- ================================================
-- TABELA: tenants (Empreendedores assinantes)
-- ================================================
CREATE TABLE IF NOT EXISTS tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  whatsapp TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  business_name TEXT,
  business_type TEXT,
  working_hours JSONB DEFAULT '{
    "seg": ["08:00","18:00"],
    "ter": ["08:00","18:00"],
    "qua": ["08:00","18:00"],
    "qui": ["08:00","18:00"],
    "sex": ["08:00","18:00"],
    "sab": null,
    "dom": null
  }',
  slot_duration INT DEFAULT 60,
  google_calendar_id TEXT,
  evolution_instance TEXT,
  plan TEXT DEFAULT 'free',
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================
-- TABELA: clients (Clientes dos empreendedores)
-- ================================================
CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT,
  whatsapp TEXT NOT NULL,
  email TEXT,
  notes TEXT,
  total_appointments INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, whatsapp)
);

-- ================================================
-- TABELA: appointments (Agendamentos)
-- ================================================
CREATE TABLE IF NOT EXISTS appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  service TEXT NOT NULL,
  scheduled_at TIMESTAMPTZ NOT NULL,
  duration INT DEFAULT 60,
  status TEXT DEFAULT 'confirmed'
    CHECK (status IN ('confirmed','pending','cancelled','rescheduled','completed','no_show')),
  notes TEXT,
  google_event_id TEXT,
  reminder_sent BOOLEAN DEFAULT FALSE,
  source TEXT DEFAULT 'whatsapp'
    CHECK (source IN ('whatsapp','dashboard','manual')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================
-- TABELA: conversations (Estado do chatbot)
-- ================================================
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  client_whatsapp TEXT NOT NULL,
  state TEXT DEFAULT 'idle',
  context JSONB DEFAULT '{}',
  last_message TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, client_whatsapp)
);

-- ================================================
-- TABELA: errors_log (Log de erros dos fluxos)
-- ================================================
CREATE TABLE IF NOT EXISTS errors_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  flow_name TEXT,
  error_message TEXT,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================
-- INDEXES
-- ================================================
CREATE INDEX IF NOT EXISTS idx_appointments_tenant_date
  ON appointments(tenant_id, scheduled_at);

CREATE INDEX IF NOT EXISTS idx_appointments_status
  ON appointments(tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_appointments_reminder
  ON appointments(reminder_sent, scheduled_at)
  WHERE status = 'confirmed' AND reminder_sent = FALSE;

CREATE INDEX IF NOT EXISTS idx_conversations_lookup
  ON conversations(tenant_id, client_whatsapp);

-- ================================================
-- TRIGGER: atualiza updated_at automaticamente
-- ================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_appointments_updated_at
  BEFORE UPDATE ON appointments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
