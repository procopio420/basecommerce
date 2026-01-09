# Arquitetura do Sistema

## Visao Geral

Plataforma SaaS multi-tenant e multi-vertical para comercio. Cada vertical (ex: materiais de construcao) tem sua propria aplicacao que consume engines horizontais reutilizaveis.

## Diagrama Logico

```
┌─────────────────────────────────────────────────────────────────┐
│                         Nginx                                    │
│              (Reverse Proxy + Multi-tenant Routing)              │
│         *.basecommerce.com.br → X-Tenant-Slug header             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Verticals Layer                               │
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐   │
│   │         Construction Vertical (FastAPI)                 │   │
│   │  ┌─────────────┐  ┌─────────────┐                      │   │
│   │  │  REST API   │  │  HTMX Web   │                      │   │
│   │  │  /api/v1/*  │  │  /web/*     │                      │   │
│   │  └─────────────┘  └─────────────┘                      │   │
│   │  ┌─────────────────────────────────────────────────┐   │   │
│   │  │ Domain / Application / Models / Schemas         │   │   │
│   │  └─────────────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────────────┘   │
│                                                                  │
│   (Futuras verticais: alimentacao, varejo, etc.)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ Events (Outbox Pattern)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Event Infrastructure                           │
│                                                                  │
│   ┌────────────────┐       ┌────────────────┐                   │
│   │  Outbox Relay  │ ───→  │ Redis Streams  │                   │
│   │  (DB Polling)  │       │ (Event Bus)    │                   │
│   └────────────────┘       └───────┬────────┘                   │
│                                    │                             │
└────────────────────────────────────┼────────────────────────────┘
                                     │ XREADGROUP
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Horizontal Engines                             │
│                                                                  │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│   │ Stock          │  │ Pricing &      │  │ Delivery &     │   │
│   │ Intelligence   │  │ Supplier       │  │ Fulfillment    │   │
│   └────────────────┘  └────────────────┘  └────────────────┘   │
│                                                                  │
│   ┌────────────────┐                                            │
│   │ Sales          │                                            │
│   │ Intelligence   │                                            │
│   └────────────────┘                                            │
│                                                                  │
│   - Consomem eventos via Redis Streams                          │
│   - Escrevem em engine-owned tables                              │
│   - NAO importam codigo de verticais                             │
└────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL                                  │
│                 (Multi-tenant por tenant_id)                     │
│                                                                  │
│   - Tabelas de verticais (cotacoes, pedidos, etc.)              │
│   - Tabelas de engines (engine_*, sugestoes, alertas)            │
│   - Event outbox para Outbox Pattern                             │
└─────────────────────────────────────────────────────────────────┘
```

## Principais Entidades

### Tenant (Loja)
- Representa uma loja ou empresa cliente
- Cada tenant tem isolamento completo de dados
- Resolvido via subdomain (ex: `loja.basecommerce.com.br`)

### Cliente
- PF (Pessoa Fisica) ou PJ (Pessoa Juridica)
- Vinculado a um tenant
- Pode ter multiplas obras

### Obra (Opcional)
- Vinculada a um cliente
- Permite precos diferenciados por obra

### Produto
- Catalogo de produtos da loja
- Preco base por produto
- Vinculado ao tenant

### Cotacao
- Lista de produtos com quantidades
- Regras de preco aplicadas
- Status: rascunho → enviada → aprovada → convertida
- Historico versionado

### Pedido
- Convertido de uma cotacao
- Representa um pedido confirmado
- Status de entrega basico

## Fluxo de Dados

1. **Criacao de Cotacao**
   - Seleciona cliente (e opcionalmente obra)
   - Adiciona produtos com quantidades
   - Aplica regras de preco (desconto)
   - Salva como rascunho

2. **Envio de Cotacao**
   - Marca status como "enviada"
   - Cliente visualiza (futuro)

3. **Aprovacao**
   - Cliente aprova (manual ou futuro sistema)

4. **Conversao em Pedido**
   - Um clique converte cotacao aprovada em pedido
   - Pedido herda todos os itens da cotacao
   - Evento emitido para engines (via outbox)

## Multi-tenant

**Estrategia**: Subdomain + Tenant ID em todas as tabelas + Middleware

- Nginx resolve subdomain e injeta `X-Tenant-Slug` header
- Middleware resolve tenant do header ou Host
- Todas as queries sao filtradas por `tenant_id`
- Isolamento garantido no nivel da aplicacao

## Event-Driven Architecture

**Padrao**: Outbox Pattern + Redis Streams

1. Vertical escreve evento na tabela `event_outbox` (mesma transacao)
2. Outbox Relay faz polling e publica no Redis Streams
3. Engines consomem via XREADGROUP (consumer groups)
4. Idempotencia garantida via `engine_processed_events`

## Seguranca

- JWT para autenticacao
- Tenant isolation obrigatorio
- Validacao de dados em todas as entradas
- Cookies HttpOnly para web
- HTTPS em producao
