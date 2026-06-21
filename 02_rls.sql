-- AgendAI — Row Level Security (RLS)
-- Execute APÓS o 01_schema.sql
-- Garante que cada tenant só acessa seus próprios dados

-- ================================================
-- HABILITAR RLS EM TODAS AS TABELAS
-- ================================================
ALTER TABLE tenants       ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients       ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments  ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE errors_log    ENABLE ROW LEVEL SECURITY;


-- ================================================
-- FUNÇÃO AUXILIAR: retorna o tenant_id do usuário
-- autenticado via Supabase Auth
-- ================================================
CREATE OR REPLACE FUNCTION auth_tenant_id()
RETURNS UUID
LANGUAGE SQL
STABLE
SECURITY DEFINER
AS $$
  SELECT id FROM tenants WHERE email = auth.email() LIMIT 1;
$$;


-- ================================================
-- TABELA: tenants
-- ================================================

-- Cada usuário lê apenas o próprio perfil
CREATE POLICY "tenant: leitura própria"
  ON tenants FOR SELECT
  USING (email = auth.email());

-- Cada usuário atualiza apenas o próprio perfil
CREATE POLICY "tenant: atualização própria"
  ON tenants FOR UPDATE
  USING (email = auth.email())
  WITH CHECK (email = auth.email());

-- Inserção livre (registro via sign-up)
CREATE POLICY "tenant: inserção pública"
  ON tenants FOR INSERT
  WITH CHECK (true);

-- Deleção bloqueada para usuários comuns (apenas service_role pode deletar)
-- (sem CREATE POLICY de DELETE = nenhum usuário pode deletar via client)


-- ================================================
-- TABELA: clients
-- ================================================

CREATE POLICY "clients: leitura pelo tenant"
  ON clients FOR SELECT
  USING (tenant_id = auth_tenant_id());

CREATE POLICY "clients: inserção pelo tenant"
  ON clients FOR INSERT
  WITH CHECK (tenant_id = auth_tenant_id());

CREATE POLICY "clients: atualização pelo tenant"
  ON clients FOR UPDATE
  USING (tenant_id = auth_tenant_id())
  WITH CHECK (tenant_id = auth_tenant_id());

CREATE POLICY "clients: deleção pelo tenant"
  ON clients FOR DELETE
  USING (tenant_id = auth_tenant_id());


-- ================================================
-- TABELA: appointments
-- ================================================

CREATE POLICY "appointments: leitura pelo tenant"
  ON appointments FOR SELECT
  USING (tenant_id = auth_tenant_id());

CREATE POLICY "appointments: inserção pelo tenant"
  ON appointments FOR INSERT
  WITH CHECK (tenant_id = auth_tenant_id());

CREATE POLICY "appointments: atualização pelo tenant"
  ON appointments FOR UPDATE
  USING (tenant_id = auth_tenant_id())
  WITH CHECK (tenant_id = auth_tenant_id());

CREATE POLICY "appointments: deleção pelo tenant"
  ON appointments FOR DELETE
  USING (tenant_id = auth_tenant_id());


-- ================================================
-- TABELA: conversations
-- ================================================

CREATE POLICY "conversations: leitura pelo tenant"
  ON conversations FOR SELECT
  USING (tenant_id = auth_tenant_id());

CREATE POLICY "conversations: inserção pelo tenant"
  ON conversations FOR INSERT
  WITH CHECK (tenant_id = auth_tenant_id());

CREATE POLICY "conversations: atualização pelo tenant"
  ON conversations FOR UPDATE
  USING (tenant_id = auth_tenant_id())
  WITH CHECK (tenant_id = auth_tenant_id());

CREATE POLICY "conversations: deleção pelo tenant"
  ON conversations FOR DELETE
  USING (tenant_id = auth_tenant_id());


-- ================================================
-- TABELA: errors_log
-- ================================================

-- Tenants só veem os próprios erros
CREATE POLICY "errors_log: leitura pelo tenant"
  ON errors_log FOR SELECT
  USING (tenant_id = auth_tenant_id());

-- Apenas service_role pode inserir (chamado pelos fluxos n8n via backend)
-- Nenhuma policy de INSERT para usuários autenticados comuns


-- ================================================
-- ACESSO DO SERVICE_ROLE (n8n e backend)
-- O service_role bypassa RLS automaticamente no Supabase.
-- Use a SUPABASE_SERVICE_ROLE_KEY nos fluxos n8n para
-- operações como:
--   - Criar/atualizar agendamentos via bot WhatsApp
--   - Inserir registros em errors_log
--   - Consultas cross-tenant para administração
-- NUNCA exponha a service_role_key no frontend.
-- ================================================


-- ================================================
-- VERIFICAÇÃO: listar todas as policies criadas
-- ================================================
SELECT
  schemaname,
  tablename,
  policyname,
  cmd,
  qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, cmd;
