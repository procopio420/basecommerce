# Documentacao BaseCommerce

## Tecnico

| # | Documento | Descricao |
|---|-----------|-----------|
| 01 | [01-overview.md](01-overview.md) | Visao geral da plataforma |
| 02 | [02-architecture.md](02-architecture.md) | Arquitetura: verticais, engines, eventos |
| 03 | [03-infrastructure.md](03-infrastructure.md) | Infra: droplets, Nginx, Redis, Postgres |
| 04 | [04-dev-setup.md](04-dev-setup.md) | Setup de desenvolvimento local |
| 05 | [05-deploy.md](05-deploy.md) | Deploy em producao |
| 06 | [06-multi-tenant.md](06-multi-tenant.md) | Multi-tenancy via subdomain |
| 07 | [07-events-engines.md](07-events-engines.md) | Eventos e engines horizontais |
| 08 | [08-scalability.md](08-scalability.md) | Escalabilidade (1000 clientes) |

## Produto

| Documento | Descricao |
|-----------|-----------|
| [product/vision.md](product/vision.md) | Visao do produto |
| [product/domain-model.md](product/domain-model.md) | Entidades e relacoes |
| [product/user-roles.md](product/user-roles.md) | Papeis e permissoes |
| [product/core-flows.md](product/core-flows.md) | Fluxos principais |
| [product/modules-phases.md](product/modules-phases.md) | Roadmap |
| [product/non-goals.md](product/non-goals.md) | O que NAO fazer |
| [product/risks.md](product/risks.md) | Premissas e riscos |
| [product/metrics.md](product/metrics.md) | Metricas de sucesso |

## Engines

| Documento | Responsabilidade |
|-----------|------------------|
| [engine/stock.md](engine/stock.md) | O QUE/QUANDO/QUANTO comprar |
| [engine/sales.md](engine/sales.md) | Aumentar valor da venda |
| [engine/pricing.md](engine/pricing.md) | DE QUEM comprar, A QUE CUSTO |
| [engine/delivery.md](engine/delivery.md) | Pedido → Entrega |
| [engine/api-contracts.md](engine/api-contracts.md) | APIs dos engines |

## Referencia

| Documento | Descricao |
|-----------|-----------|
| [ref/database-schema.md](ref/database-schema.md) | Schema SQL |
| [ref/event-contracts.md](ref/event-contracts.md) | Tipos de eventos |
| [ref/ux-flow.md](ref/ux-flow.md) | Fluxo de UX |

## Leitura Rapida

1. [01-overview.md](01-overview.md)
2. [02-architecture.md](02-architecture.md)
3. [08-scalability.md](08-scalability.md)
