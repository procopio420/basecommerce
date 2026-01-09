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
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────┐     ┌──────────────────────────────────────┐
│    Auth Service      │     │           Verticals Layer            │
│    (FastAPI :8001)   │     │                                      │
│                      │     │   ┌──────────────────────────────┐   │
│  - /auth/login       │     │   │  Construction Vertical       │   │
│  - /auth/logout      │     │   │  (FastAPI :8000)              │   │
│  - /auth/me          │     │   │                              │   │
│  - /tenant.json      │     │   │  - /api/v1/* (REST)          │   │
│                      │     │   │  - /web/*    (HTMX)          │   │
│  Owns:               │     │   └──────────────────────────────┘   │
│  - Tenant model      │     │                                      │
│  - User model        │     │   Uses: UserClaims from JWT          │
│  - TenantBranding    │     │   (no User/Tenant models)            │
└──────────────────────┘     └──────────────────────────────────────┘
              │                             │
              └──────────────┬──────────────┘
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
│   - Tabelas de auth (tenants, users, tenant_branding)           │
│   - Tabelas de verticais (cotacoes, pedidos, etc.)              │
│   - Tabelas de engines (engine_*, sugestoes, alertas)            │
│   - Event outbox para Outbox Pattern                             │
└─────────────────────────────────────────────────────────────────┘
```

## Auth Service

O Auth Service e centralizado e responsavel por:

- **Autenticacao**: Login/logout via JWT
- **Tenant Resolution**: Endpoint `/tenant.json` retorna branding do tenant
- **User Management**: Modelos Tenant, User, TenantBranding

### Endpoints

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/auth/login` | GET | Pagina de login (HTML) |
| `/auth/login` | POST | Login JSON, retorna JWT |
| `/auth/login/form` | POST | Login form, set cookie |
| `/auth/logout` | GET | Clear cookie, redirect |
| `/auth/me` | GET | User info (Bearer/cookie) |
| `/tenant.json` | GET | Branding (via X-Tenant-Slug) |
| `/auth/validate` | GET | Valida token |

### Fluxo de Login

```
1. Usuario acessa /web/dashboard
2. Nginx redireciona /web/login → /auth/login
3. Auth Service renderiza pagina de login
4. Usuario submete form para /auth/login/form
5. Auth Service valida credenciais
6. Auth Service cria JWT com claims:
   - sub: user_id
   - tenant_id: tenant_id
   - email: user_email
   - role: user_role
7. Auth Service seta cookie httponly
8. Redirect para /web/dashboard
9. Vertical extrai claims do JWT (sem query ao banco)
```

## Principais Entidades

### Tenant (Loja)
- Representa uma loja ou empresa cliente
- Cada tenant tem isolamento completo de dados
- Resolvido via subdomain (ex: `loja.basecommerce.com.br`)
- **Gerenciado pelo Auth Service**

### User
- Usuario dentro de um tenant
- Roles: admin, vendedor
- **Gerenciado pelo Auth Service**

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

**Estrategia**: Subdomain + JWT Claims + Middleware

- Nginx resolve subdomain e injeta `X-Tenant-Slug` header
- Auth Service resolve tenant do header e gera JWT
- JWT contem `tenant_id` nos claims
- Vertical extrai `tenant_id` do JWT (sem query ao banco)
- Todas as queries sao filtradas por `tenant_id`

## Event-Driven Architecture

**Padrao**: Outbox Pattern + Redis Streams

1. Vertical escreve evento na tabela `event_outbox` (mesma transacao)
2. Outbox Relay faz polling e publica no Redis Streams
3. Engines consomem via XREADGROUP (consumer groups)
4. Idempotencia garantida via `engine_processed_events`

## Seguranca

- JWT para autenticacao (criado pelo Auth Service)
- Tenant isolation via JWT claims
- Validacao de dados em todas as entradas
- Cookies HttpOnly para web
- HTTPS em producao
- Auth Service centraliza gestao de usuarios
