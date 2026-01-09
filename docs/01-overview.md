# BaseCommerce - Visao Geral da Plataforma

## O que e

BaseCommerce e uma **plataforma SaaS multi-tenant** para verticais de comercio. A primeira vertical implementada e para lojas de materiais de construcao no Brasil.

## Arquitetura em uma frase

> Verticais publicam eventos → Engines horizontais consomem → Dados ficam isolados por tenant.

## Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX                                    │
│              *.basecommerce.com.br → X-Tenant-Slug               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VERTICAIS                                   │
│                                                                  │
│   Construction Vertical (apps/verticals/construction/)          │
│   ├── API REST (/api/v1/*)                                      │
│   ├── Web HTMX (/web/*)                                         │
│   └── Domain (cotacoes, pedidos, clientes, produtos)            │
│                                                                  │
│   Futuras: alimentacao, varejo, etc.                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Eventos (Outbox Pattern)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRA DE EVENTOS                              │
│                                                                  │
│   Outbox Relay (DB → Redis Streams)                             │
│   Redis Streams (Event Bus)                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ XREADGROUP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ENGINES HORIZONTAIS                             │
│                                                                  │
│   Stock Intelligence    - O QUE/QUANDO/QUANTO comprar           │
│   Sales Intelligence    - Sugestoes de venda                     │
│   Pricing & Supplier    - DE QUEM comprar, A QUE CUSTO          │
│   Delivery & Fulfillment - Pedido → Entrega → Confirmacao        │
│                                                                  │
│   Escrevem em engine-owned tables, NAO importam verticais       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      POSTGRESQL                                  │
│              Multi-tenant por tenant_id em todas as tabelas     │
└─────────────────────────────────────────────────────────────────┘
```

## Regras de Ouro

1. **Verticais NAO importam engines** - comunicacao via eventos
2. **Engines NAO importam verticais** - so usam basecore + engines_core
3. **Tenant e resolvido pelo Nginx** - header X-Tenant-Slug
4. **Eventos sao a unica comunicacao** - outbox pattern garante entrega
5. **VPS-only** - sem k8s, sem serverless

## Estrutura de Pastas

```
basecommerce/
├── apps/
│   ├── auth/                    # Servico de auth (placeholder)
│   ├── engines/                 # Worker que consome eventos
│   ├── outbox-relay/            # Relay DB → Redis Streams
│   └── verticals/
│       └── construction/        # Vertical de materiais
├── packages/
│   ├── basecore/               # Infra compartilhada
│   └── engines_core/           # Logica dos engines
├── infra/
│   └── nginx/                  # Config Nginx multi-tenant
└── docs/                       # Esta documentacao
```

## Proximos Passos

- [Arquitetura detalhada](01_architecture.md)
- [Setup local](03_dev_setup.md)
- [Deploy em producao](04_deploy.md)
- [Multi-tenancy](05_multi_tenant.md)
- [Eventos e Engines](06_events_and_engines.md)
- [Escalabilidade](07_scalability.md)

