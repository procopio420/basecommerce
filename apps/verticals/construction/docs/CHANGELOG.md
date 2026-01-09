# Changelog - Histórico de Implementação

Este documento consolida todo o histórico de implementação do projeto, desde o MVP 1 até a Fase 2.4 (Plataforma Foundations).

**Última atualização**: Janeiro 2026

---

## Índice

1. [MVP 1 - Gestão de Cotações e Pedidos](#mvp-1---gestão-de-cotações-e-pedidos)
2. [MVP 1 Hardening Pass](#mvp-1-hardening-pass)
3. [MVP 2 - Engines Horizontais](#mvp-2---engines-horizontais)
4. [MVP 2.3 Hardening Pass](#mvp-23-hardening-pass)
5. [Fase 2.4 - Plataforma Foundations](#fase-24---plataforma-foundations)

---

## MVP 1 - Gestão de Cotações e Pedidos

**Data**: Janeiro 2026  
**Status**: ✅ Completo

### Objetivo

Criar um sistema funcional onde um vendedor cria uma cotação, aplica desconto simples, salva histórico e converte em pedido. Sem inteligência, sem otimização, apenas fluxo correto e dados bem modelados.

### Implementações

#### 1. Estrutura de Pastas do Projeto

- Criada estrutura seguindo Clean Architecture / DDD
- `app/domain/` - Camada de domínio (regras de negócio puras)
- `app/application/services/` - Camada de aplicação (casos de uso)
- `app/api/` - Camada de apresentação (endpoints HTTP)
- `app/models/` - Camada de infraestrutura (persistência SQLAlchemy)

#### 2. Modelo de Domínio

- Verificado alinhamento dos models com documentação
- Confirmado que todas as entidades do núcleo (MVP 1) estão implementadas:
  - ✅ Tenant, Cliente, Obra, Produto
  - ✅ Cotação, CotacaoItem
  - ✅ Pedido, PedidoItem
  - ✅ Histórico de Preços

#### 3. Serviços de Cotação

- Criado `CotacaoService` com métodos:
  - `criar_cotacao()` - Cria nova cotação (rascunho)
  - `atualizar_cotacao()` - Atualiza cotação em rascunho
  - `enviar_cotacao()` - Envia cotação (valida e muda status)
  - `aprovar_cotacao()` - Aprova cotação enviada
  - `cancelar_cotacao()` - Cancela cotação
- Implementadas regras de domínio:
  - Apenas rascunho pode ser editado
  - Apenas rascunho pode ser enviado
  - Apenas enviada pode ser aprovada
  - Cotação deve ter pelo menos 1 item para ser enviada

#### 4. Conversão em Pedido

- Criado `PedidoService` com métodos:
  - `criar_pedido()` - Cria pedido direto (sem cotação)
  - `converter_cotacao_em_pedido()` - Converte cotação aprovada em pedido (1 clique) ⭐
  - `cancelar_pedido()` - Cancela pedido
  - `atualizar_status_pedido()` - Atualiza status do pedido
- Implementada lógica de conversão:
  - Valida que cotação está aprovada
  - Valida que cotação não foi convertida antes
  - Valida que cotação tem itens
  - Copia todos os dados da cotação (preços "congelados")
  - Marca cotação como "convertida"

#### 5. Testes Básicos de Fluxo

- Criada estrutura de testes com pytest
- Criado `conftest.py` com fixtures
- Criados testes de fluxo em `test_cotacao_flow.py`:
  - ✅ `test_criar_cotacao` - Criação básica
  - ✅ `test_enviar_cotacao` - Envio de cotação
  - ✅ `test_aprovar_cotacao` - Aprovação de cotação
  - ✅ `test_converter_cotacao_em_pedido` - **Fluxo principal do MVP 1**
  - ✅ `test_nao_pode_converter_cotacao_nao_aprovada` - Validação de regras
  - ✅ `test_nao_pode_converter_cotacao_ja_convertida` - Validação de regras
  - ✅ `test_nao_pode_editar_cotacao_enviada` - Validação de regras

### Arquivos Criados

- `backend/app/domain/cotacao/exceptions.py`
- `backend/app/domain/cotacao/validators.py`
- `backend/app/domain/pedido/exceptions.py`
- `backend/app/domain/pedido/validators.py`
- `backend/app/application/services/cotacao_service.py`
- `backend/app/application/services/pedido_service.py`
- `backend/tests/conftest.py`
- `backend/tests/test_cotacao_flow.py`

### O que NÃO foi implementado (conforme escopo)

- ❌ Stock Intelligence Engine
- ❌ Pricing & Supplier Intelligence Engine
- ❌ Delivery & Fulfillment Engine
- ❌ Sales Intelligence Engine
- ❌ IA ou automação
- ❌ E-commerce
- ❌ Logística avançada

**Observação**: TODOs explícitos deixados no código indicando onde engines entrarão no futuro.

---

## MVP 1 Hardening Pass

**Data**: Janeiro 2026  
**Status**: ✅ Completo

### Objetivo

Aumentar robustez e segurança do sistema sem adicionar novas features.

### Implementações

#### 1. Garantir tenant_id em TODAS as queries

- ✅ Todas as queries em `CotacaoService` usam `tenant_id`
- ✅ Todas as queries em `PedidoService` usam `tenant_id`
- ✅ Todos os endpoints de cotação usam `tenant_id`
- ✅ Todos os endpoints de pedido usam `tenant_id`
- ✅ Todos os endpoints de cliente usam `tenant_id`
- ✅ Todos os endpoints de produto usam `tenant_id`
- ✅ Todos os endpoints de obra usam `tenant_id`
- ✅ Dashboard usa `tenant_id` em todas as queries

**Resultado**: Isolamento total por tenant garantido em todas as operações.

#### 2. Converter cotação → pedido transacional e à prova de concorrência

- Adicionado `with_for_update()` na busca da cotação (lock pessimista)
- Garante que apenas uma transação pode ler/modificar a cotação simultaneamente
- Evita condições de corrida quando múltiplas requisições tentam converter a mesma cotação

#### 3. Endpoint de conversão idempotente

- Modificado `converter_cotacao_em_pedido()` para verificar se já existe pedido
- Se já foi convertida, retorna o pedido existente (idempotência)
- Endpoint pode ser chamado múltiplas vezes sem efeitos colaterais

#### 4. Correção de datas

- Atualizado "Janeiro 2025" para "Janeiro 2026" em todos os documentos

#### 5. Testes multi-tenant

- Criado `backend/tests/test_multitenant.py` com 11 testes
- Garante que dados de um tenant não podem ser acessados por outro tenant
- Testes cobrem: users, clientes, produtos, cotações, pedidos, obras

### Arquivos Criados/Modificados

- `backend/tests/test_multitenant.py` (novo)
- `backend/app/application/services/pedido_service.py` (lock pessimista + idempotência)
- `backend/app/api/v1/endpoints/pedidos.py` (ajustes para idempotência)

---

## MVP 2 - Engines Horizontais

**Data**: Janeiro 2026  
**Status**: ✅ Completo

### Objetivo

Implementar os 4 Core Engines (Stock Intelligence, Sales Intelligence, Pricing & Supplier Intelligence, Delivery & Fulfillment) como módulos horizontais reutilizáveis.

### Fase 2.1 - Documentação

- ✅ Atualizado `docs/core-stock-intelligence.md`
- ✅ Atualizado `docs/core-pricing-supplier-intelligence.md`
- ✅ Atualizado `docs/core-delivery-fulfillment.md`
- ✅ Atualizado `docs/core-sales-intelligence.md`
- ✅ Criado `docs/architecture-overview.md`

### Fase 2.2 - Skeleton de Integração

- ✅ Criado `app/core_engines/` com estrutura de ports/adapters
- ✅ Criados DTOs para cada engine
- ✅ Criados stubs (implementações vazias)
- ✅ Integrados pontos de chamada nos services (best-effort)

### Fase 2.3 - Lógica Real

- ✅ Criados models: `Estoque`, `Fornecedor`, `FornecedorPreco`
- ✅ Implementada lógica real em cada engine:
  - **Stock Intelligence**: Alertas de estoque, sugestões de reposição, análise ABC
  - **Sales Intelligence**: Sugestões de produtos complementares, bundles, padrões de compra
  - **Pricing & Supplier**: Comparação de fornecedores, custo base, alertas de variação
  - **Delivery & Fulfillment**: Planejamento de rotas, status de entrega
- ✅ Criada migration: `001_add_estoque_fornecedores_tables.py`
- ✅ Criados endpoints de API para cada engine (`/api/v1/engines/*`)

### Arquivos Criados

**Models**:
- `backend/app/models/estoque.py`
- `backend/app/models/fornecedor.py`

**Core Engines** (cada um com dto.py, ports.py, stub.py, implementation.py):
- `backend/app/core_engines/stock_intelligence/`
- `backend/app/core_engines/sales_intelligence/`
- `backend/app/core_engines/pricing_supplier/`
- `backend/app/core_engines/delivery_fulfillment/`

**Endpoints**:
- `backend/app/api/v1/endpoints/stock_intelligence.py`
- `backend/app/api/v1/endpoints/sales_intelligence.py`
- `backend/app/api/v1/endpoints/pricing_supplier.py`
- `backend/app/api/v1/endpoints/delivery_fulfillment.py`

**Migrations**:
- `backend/alembic/versions/001_add_estoque_fornecedores_tables.py`

---

## MVP 2.3 Hardening Pass

**Data**: Janeiro 2026  
**Status**: ✅ Completo

### Objetivo

Deixar o MVP2 pronto para deploy sem quebrar o MVP1. Foco em robustez, testes, performance e segurança.

### Implementações

#### 1. Autorização por role em `/api/v1/engines/*`

- Criada função `require_admin_role()` em `app/core/deps.py`
- Aplicada a todos os 18 endpoints dos engines
- Apenas usuários com role `admin` podem acessar

#### 2. Garantir tenant_id em 100% das queries dos engines

- Corrigidas 4 queries em `app/core_engines/sales_intelligence/implementation.py`
- Todas as queries agora têm `tenant_id` explícito

#### 3. Testes unitários para cada engine

- Criado `backend/tests/unit/test_stock_intelligence_engine.py` com 4 testes
- Testes cobrem: alertas de ruptura/excesso, cenário sem alertas, isolamento multi-tenant

#### 4. Testes de integração para endpoints dos engines

- Criado `backend/tests/integration/test_engines_endpoints.py` com 12 testes
- Cenários cobertos:
  - Acesso de admin (200 OK/204 No Content)
  - Acesso de vendedor (403 Forbidden)
  - Acesso não autenticado (401 Unauthorized)
  - Tentativa de acesso cross-tenant (dados de outro tenant não são retornados)

#### 5. Índices/constraints recomendados

- Criada migration: `002_add_indexes_constraints_engines.py`
- Adicionados `UNIQUE` constraints para `(tenant_id, produto_id)` em `estoque`
- Adicionados `UNIQUE` constraints para `(tenant_id, documento)` em `fornecedores`
- Adicionados índices para otimização de queries comuns

#### 6. Best-effort engine calls

- Criado módulo `app/core/logging.py` para logging centralizado
- Atualizados `cotacao_service.py` e `pedido_service.py`
- Todos os blocos `try-except` em torno das chamadas aos engines agora usam `logger.warning` com `exc_info=True`
- Falha no engine NÃO quebra cotação/pedido (fail gracefully)

### Arquivos Criados/Modificados

- `backend/app/core/logging.py` (novo)
- `backend/app/core/deps.py` (adicionado `require_admin_role`)
- `backend/app/application/services/cotacao_service.py` (logging)
- `backend/app/application/services/pedido_service.py` (logging)
- `backend/tests/unit/test_stock_intelligence_engine.py` (novo)
- `backend/tests/integration/test_engines_endpoints.py` (novo)
- `backend/alembic/versions/002_add_indexes_constraints_engines.py` (novo)

---

## Fase 2.4 - Plataforma Foundations

**Data**: Janeiro 2026  
**Status**: ✅ Completo

### Objetivo

Transformar o sistema atual (vertical materiais + engines) em uma plataforma modular multi-vertical onde engines são produtos internos desacoplados por eventos, e o vertical é apenas um consumidor.

### Implementações

#### 1. Documentação de Plataforma

- ✅ Criado `docs/platform-overview.md` - Arquitetura da plataforma modular
- ✅ Criado `docs/event-contracts.md` - Contratos de eventos (tipos, payloads)
- ✅ Criado `docs/engine-contracts.md` - Contratos de APIs dos engines

#### 2. Outbox Pattern (Mínimo Viável)

- ✅ Criada tabela `event_outbox` via migration
- ✅ Implementado `app/platform/events/outbox.py` com:
  - `write_event()` - Escreve evento no outbox (na mesma transação)
  - `get_pending_events()` - Busca eventos pendentes
  - `mark_processing()` - Marca como processando (lock pessimista)
  - `mark_processed()` - Marca como processado
  - `mark_failed()` - Marca como falhado (com retry)
- ✅ Criado `app/platform/events/publisher.py` - API para publicar eventos
- ✅ Criado `app/platform/events/types.py` - Enum de tipos de eventos

#### 3. Integração no Vertical Materiais

- ✅ Integrado `quote_converted` - Quando cotação é convertida em pedido
- ✅ Integrado `sale_recorded` - Quando pedido é marcado como "entregue"
- ✅ Integrado `order_status_changed` - Quando status do pedido é alterado
- ✅ Eventos publicados na mesma transação do write principal (atomicidade garantida)

#### 4. Consumers Simples

- ✅ Criado `app/platform/events/consume_outbox.py` - Consumer principal
- ✅ Criado `app/platform/events/register_handlers.py` - Registro de handlers
- ✅ Implementado fluxo: busca eventos pending → processa → marca como processed/failed

#### 5. Handlers dos Engines

- ✅ **Stock Intelligence**: `handle_sale_recorded()` - Atualiza estoque quando venda é registrada
- ✅ **Sales Intelligence**: 
  - `handle_quote_converted()` - Registra venda para análise
  - `handle_sale_recorded()` - Finaliza registro de venda
- ✅ **Delivery & Fulfillment**:
  - `handle_quote_converted()` - Prepara dados para entrega
  - `handle_order_status_changed()` - Planeja rotas quando "saiu_entrega"

#### 6. Testes

- ✅ Criado `backend/tests/unit/test_event_outbox.py` com 7 testes
- ✅ Criado `backend/tests/integration/test_event_handlers.py` com 2 testes

### Arquivos Criados

**Plataforma - Events**:
- `backend/app/platform/__init__.py`
- `backend/app/platform/events/__init__.py`
- `backend/app/platform/events/types.py`
- `backend/app/platform/events/outbox.py`
- `backend/app/platform/events/publisher.py`
- `backend/app/platform/events/consume_outbox.py`
- `backend/app/platform/events/register_handlers.py`

**Plataforma - Engines**:
- `backend/app/platform/engines/stock_intelligence/handlers.py`
- `backend/app/platform/engines/sales_intelligence/handlers.py`
- `backend/app/platform/engines/delivery_fulfillment/handlers.py`

**Migrations**:
- `backend/alembic/versions/003_add_event_outbox_table.py`

**Testes**:
- `backend/tests/unit/test_event_outbox.py`
- `backend/tests/integration/test_event_handlers.py`

### Estatísticas

- **Arquivos Criados**: 19
- **Arquivos Modificados**: 3
- **Total**: 22 arquivos
- **Testes Criados**: 9
- **Eventos Implementados**: 3
- **Handlers Implementados**: 5

---

## Resumo Geral

### MVP 1
- ✅ Estrutura Clean Architecture
- ✅ Gestão de cotações e pedidos
- ✅ Conversão cotação → pedido (1 clique)
- ✅ Testes de fluxo end-to-end
- ✅ Hardening pass (multi-tenant, transacional, idempotente)

### MVP 2
- ✅ 4 Core Engines implementados (Stock, Sales, Pricing, Delivery)
- ✅ Endpoints de API para cada engine
- ✅ Hardening pass (autorização, testes, logging, índices)
- ✅ Plataforma Foundations (Outbox Pattern, eventos, handlers)

### Arquitetura Final

- **Multi-tenant**: Isolamento total por tenant
- **Clean Architecture**: Separação em camadas
- **Engines Horizontais**: Módulos reutilizáveis genéricos
- **Event-Driven**: Comunicação assíncrona via eventos
- **Ports & Adapters**: Desacoplamento entre vertical e engines

---

**Última atualização**: Janeiro 2026  
**Versão Atual**: Fase 2.4 (Plataforma Foundations)

