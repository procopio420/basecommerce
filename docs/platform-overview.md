# Visão Geral da Plataforma Modular Multi-Vertical

## Versão: 2.4 - Plataforma Foundations

**Data**: Janeiro 2026

---

## 🎯 Objetivo da Plataforma

Transformar o sistema atual (vertical materiais + engines) em uma **plataforma modular multi-vertical** onde:

- **Engines são produtos internos desacoplados** que consomem eventos
- **Verticals são consumidores** que publicam eventos e consomem serviços dos engines
- **Comunicação assíncrona** via eventos (Outbox Pattern)
- **Contratos claros** entre componentes (event contracts, API contracts)

---

## 🏗️ Arquitetura da Plataforma

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLATAFORMA (Core)                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Outbox     │  │  Consumers   │  │  Event Bus   │         │
│  │   Pattern    │  │   (Simple)   │  │   (Internal) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │           API Boundary (Internal APIs)              │       │
│  │  - Role checks (admin-only)                         │       │
│  │  - Rate limiting                                    │       │
│  │  - Versioning                                       │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   VERTICALS (Consumers)                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────┐         │
│  │  Vertical: Materiais de Construção                │         │
│  │                                                    │         │
│  │  • Publica eventos (quote_converted, sale_recorded)│         │
│  │  • Consome serviços dos engines via API          │         │
│  │  • Gerenciamento de cotações e pedidos           │         │
│  └───────────────────────────────────────────────────┘         │
│                                                                 │
│  ┌───────────────────────────────────────────────────┐         │
│  │  Vertical: [Futuro - Outro Vertical]              │         │
│  │                                                    │         │
│  │  • Publica seus próprios eventos                  │         │
│  │  • Consome serviços dos engines                   │         │
│  └───────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 ENGINES (Event Consumers)                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Stock     │  │   Sales     │  │  Pricing    │            │
│  │ Intelligence│  │ Intelligence│  │ & Supplier  │            │
│  │             │  │             │  │ Intelligence│            │
│  │ • Handler   │  │ • Handler   │  │ • Handler   │            │
│  │ • Models    │  │ • Models    │  │ • Handler   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐                                              │
│  │  Delivery   │                                              │
│  │ & Fulfillment│                                              │
│  │             │                                              │
│  │ • Handler   │                                              │
│  │ • Models    │                                              │
│  └─────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Eventos

### Publicação de Eventos (Vertical → Outbox)

```
1. Vertical executa ação de negócio (ex: converter cotação → pedido)
   ↓
2. Write principal acontece (INSERT/UPDATE na tabela de domínio)
   ↓
3. Evento é escrito na mesma transação (INSERT em event_outbox)
   ↓
4. COMMIT (garante atomicidade)
```

### Consumo de Eventos (Outbox → Engines)

```
1. Consumer lê eventos pending do event_outbox
   ↓
2. Para cada evento:
   a. Identifica event_type
   b. Roteia para handler apropriado do engine
   c. Handler processa (atualiza modelos do engine)
   d. Marca evento como processed ou failed
   ↓
3. Consumer continua processando ou aguarda intervalo
```

---

## 📦 Core vs Vertical vs Engines

### Core (Plataforma)

**Responsabilidade**: Infraestrutura e padrões comuns

**Componentes**:
- **Outbox Pattern**: Garantia de entrega de eventos (transacional)
- **Event Consumers**: Processamento assíncrono de eventos
- **API Boundary**: Controle de acesso, rate limiting, versioning
- **Event Contracts**: Definição de tipos e payloads de eventos
- **Multi-tenancy**: Isolamento de dados e segurança

**O que faz**:
- ✅ Gerencia eventos (escrita, leitura, processamento)
- ✅ Fornece contratos claros para eventos e APIs
- ✅ Garante isolamento multi-tenant
- ✅ Controla acesso e limites

**O que NÃO faz**:
- ❌ Não contém lógica de negócio específica
- ❌ Não conhece regras de verticals ou engines
- ❌ Não processa eventos diretamente (delega para handlers)

---

### Verticals (Aplicações de Negócio)

**Responsabilidade**: Lógica de negócio específica do domínio

**Componentes**:
- **Domain Models**: Entidades de negócio (Cotacao, Pedido, Cliente, etc.)
- **Application Services**: Orquestração de fluxos de negócio
- **API Endpoints**: Exposição de funcionalidades via REST
- **Event Publishers**: Publicação de eventos de domínio

**O que faz**:
- ✅ Gerencia ciclo de vida de entidades de negócio
- ✅ Publica eventos quando ações importantes acontecem
- ✅ Consome serviços dos engines via API (quando necessário)
- ✅ Mantém regras de negócio do domínio

**O que NÃO faz**:
- ❌ Não chama engines diretamente no request/response (apenas best-effort)
- ❌ Não conhece implementação interna dos engines
- ❌ Não processa eventos de outros verticals (apenas publica)

**Exemplo: Vertical "Materiais de Construção"**
- Publica: `quote_converted`, `sale_recorded`, `quote_created`
- Consome: API dos engines para obter sugestões (best-effort)

---

### Engines (Serviços Horizontais)

**Responsabilidade**: Lógica reutilizável e especializada

**Componentes**:
- **Event Handlers**: Processamento de eventos específicos
- **Domain Models**: Entidades específicas do engine (Estoque, Fornecedor, etc.)
- **Internal API**: Endpoints para consultas e configurações
- **Business Logic**: Análises, sugestões, otimizações

**O que faz**:
- ✅ Processa eventos e atualiza seus próprios modelos
- ✅ Fornece APIs para consultas e configurações
- ✅ Executa análises e gera sugestões
- ✅ Mantém estado interno baseado em eventos

**O que NÃO faz**:
- ❌ Não conhece detalhes de verticals específicos
- ❌ Não publica eventos para verticals (apenas consome)
- ❌ Não interrompe fluxo do vertical (processamento assíncrono)
- ❌ Não toma decisões finais (apenas sugere)

**Exemplo: Stock Intelligence Engine**
- Consome: `sale_recorded` (atualiza estoque)
- Fornece: API para alertas, sugestões de reposição, análise ABC

---

## 🔐 Isolamento e Segurança

### Multi-tenancy

- **Todos os componentes respeitam `tenant_id`**
- **Eventos incluem `tenant_id` no payload**
- **Handlers validam `tenant_id` antes de processar**
- **Queries sempre filtradas por `tenant_id`**

### Acesso e Permissões

- **Endpoints de Engines**: Admin-only (role check)
- **Event Publishers**: Apenas dentro do vertical (não exposto)
- **Event Consumers**: Processamento interno (não exposto)
- **Rate Limiting**: Aplicado em endpoints de engines (futuro)

---

## 📊 Benefícios da Arquitetura

### Desacoplamento

- ✅ Verticals não dependem diretamente dos engines
- ✅ Engines não conhecem verticals específicos
- ✅ Comunicação via eventos (contratos bem definidos)

### Escalabilidade

- ✅ Engines podem ser escalados independentemente
- ✅ Processamento assíncrono não bloqueia requests
- ✅ Múltiplos verticals podem usar os mesmos engines

### Evolução

- ✅ Novos verticals podem ser adicionados facilmente
- ✅ Novos engines podem ser criados sem impacto
- ✅ Contratos versionados permitem evolução incremental

### Confiabilidade

- ✅ Outbox Pattern garante entrega de eventos
- ✅ Processamento assíncrono evita falhas em cascata
- ✅ Best-effort no request/response mantém disponibilidade

---

## 🚀 Roadmap

### Fase 2.4 (Atual) - Plataforma Foundations

- ✅ Outbox Pattern (mínimo viável)
- ✅ Consumers simples (sem Celery)
- ✅ Handlers básicos para engines
- ✅ Integração incremental no vertical materiais

### Fase 2.5 (Futuro) - Event Bus Robusto

- Celery/RabbitMQ para processamento distribuído
- Dead Letter Queue para eventos com falha
- Retry policies configuráveis
- Monitoramento e métricas

### Fase 2.6 (Futuro) - Novos Verticals

- Segundo vertical (ex: equipamentos)
- Prova de conceito de multi-vertical
- Documentação de onboarding

---

**Versão**: 1.0  
**Data**: Janeiro 2026  
**Status**: 📋 Documentação Inicial - Implementação em Progresso

