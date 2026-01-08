# Módulos e Fases do Sistema

## Visão Geral

O sistema é dividido em módulos funcionais, cada um implementado em fases (MVPs). Cada módulo resolve um problema específico e pode funcionar de forma independente, mas todos se integram para formar o sistema completo.

---

## Módulo 1: Cotações (MVP 1)

### Objetivo

Permitir que vendedores criem cotações rapidamente (3 minutos) e convertam em pedidos sem retrabalho.

### Inputs

- Dados do cliente (nome, documento, contato)
- Dados da obra (opcional: nome, endereço)
- Lista de produtos (código/nome, quantidade, preço unitário)
- Regras de preço (tabela base, desconto percentual)
- Observações e validade

### Outputs

- Cotação criada (número, status, total)
- Histórico de cotações
- Cotação convertida em pedido (1 clique)
- Dashboard com métricas (cotações do dia, taxa de conversão)

### Dependências

- **Módulo 0 (Base)**: Multi-tenant, autenticação, usuários
- **Clientes**: Deve existir antes de criar cotação
- **Produtos**: Deve existir catálogo de produtos
- **Obras**: Opcional, mas comum

### KPIs

- **Tempo médio de cotação**: Reduzir de 15-20 minutos para 3-5 minutos
- **Taxa de conversão cotação → pedido**: Aumentar de ~30% para 60%+
- **Taxa de erro em cotações**: Reduzir de ~15% para <5%

### Funcionalidades Principais

- ✅ Criar cotação em 3 minutos
- ✅ Buscar cliente e produto em tempo real
- ✅ Aplicar regras simples de preço (tabela base + desconto)
- ✅ Salvar como rascunho ou enviar
- ✅ Histórico de cotações
- ✅ Converter cotação aprovada em pedido (1 clique)
- ✅ Status da cotação (rascunho, enviada, aprovada, convertida, cancelada)

### O Que NÃO Entra no MVP 1

- ❌ Envio automático de email
- ❌ Aprovação online pelo cliente
- ❌ Catálogo personalizado por cliente
- ❌ Recompra automática

### Próximos Passos (MVP 4+)

- Catálogo personalizado por cliente
- Preços negociados por cliente/obra
- Aprovação online pelo cliente
- E-commerce B2B para recompra

---

## Módulo 2: Pedidos (MVP 1 - Básico)

### Objetivo

Gerenciar pedidos criados a partir de cotações ou diretamente, com rastreamento básico de status.

### Inputs

- Dados da cotação (se convertido) ou dados diretos (cliente, produtos)
- Status do pedido
- Observações

### Outputs

- Pedido criado (número, status, total)
- Histórico de pedidos
- Status atualizado
- Dashboard com métricas (pedidos do dia, pedidos entregues)

### Dependências

- **Módulo 1 (Cotações)**: Pedidos podem vir de cotações
- **Clientes**: Deve existir antes de criar pedido
- **Produtos**: Deve existir catálogo de produtos
- **Obras**: Opcional

### KPIs

- **Tempo de criação de pedido**: Reduzir retrabalho (0 retrabalho se veio de cotação)
- **Taxa de erro em pedidos**: Reduzir de ~15% para <5%
- **Tempo médio de entrega**: Acompanhar (meta: 1-2 dias)

### Funcionalidades Principais

- ✅ Criar pedido direto ou converter de cotação
- ✅ Histórico de pedidos
- ✅ Atualizar status (pendente, em_preparacao, saiu_entrega, entregue, cancelado)
- ✅ Dashboard com pedidos do dia
- ✅ Visualizar detalhes do pedido

### O Que NÃO Entra no MVP 1

- ❌ Rastreamento GPS
- ❌ Roteirização automática
- ❌ Prova de entrega (foto, assinatura)
- ❌ Integração com transportadora

### Próximos Passos (MVP 3)

- Roteirização
- Prova de entrega
- App para motorista
- Rastreamento GPS

---

## Módulo 3: Gestão de Estoque (MVP 2)

### Objetivo

Gerenciar estoque físico do vertical de materiais de construção e consumir o Stock Intelligence Engine para obter sugestões e alertas inteligentes.

### Inputs

- Estoque atual por produto (quantidade disponível)
- Entradas/saídas de estoque (movimentação física)
- Parâmetros de reposição (tempo de reposição, segurança) - para configurar o engine
- Histórico de vendas via pedidos entregues - para enviar ao engine

### Outputs

- Estoque atual atualizado (quantidade disponível)
- Alertas de risco de ruptura (do Stock Intelligence Engine)
- Sugestões de reposição (do Stock Intelligence Engine)
- Análise ABC (do Stock Intelligence Engine)
- Relatório de estoque (itens abaixo do mínimo, itens acima do máximo)

### Dependências

- **Módulo 1 (Cotações)**: Base para contexto do negócio
- **Módulo 2 (Pedidos)**: Histórico de vendas via pedidos entregues
- **Produtos**: Deve existir catálogo de produtos
- **Histórico de Vendas**: Deve ter vendas suficientes para análise (mínimo 1-2 meses)
- **Stock Intelligence Engine (Core)**: Consome engine para obter alertas, sugestões e análise ABC

### KPIs

- **Ruptura de estoque**: Reduzir de ~20% dos itens para <5%
- **Capital parado em estoque**: Reduzir de 40-50% para <30%
- **Acurácia da sugestão**: 80%+ das sugestões são seguidas

### Funcionalidades Principais

- ✅ Gestão de estoque físico (quantidade atual, entradas/saídas)
- ✅ Atualização manual de estoque
- ✅ Integração com pedidos (atualiza estoque quando pedido é entregue)
- ✅ Interface para visualizar alertas do Stock Intelligence Engine
- ✅ Interface para visualizar sugestões de reposição do Stock Intelligence Engine
- ✅ Interface para visualizar análise ABC do Stock Intelligence Engine
- ✅ Relatório de estoque (itens abaixo do mínimo, itens acima do máximo)
- ✅ Configuração de parâmetros de reposição (para o engine)

### Como Consome o Stock Intelligence Engine

Este módulo consome o **Stock Intelligence Engine** (módulo horizontal) para obter:

- **Alertas de risco de ruptura**: Engine analisa histórico de vendas e estoque atual, detecta risco de ruptura
- **Sugestões de reposição**: Engine sugere produtos e quantidades baseadas em vendas históricas
- **Análise ABC**: Engine classifica produtos em classes A, B, C baseado em importância
- **Explicações**: Engine fornece explicações em linguagem natural de por que sugere algo

**Fluxo de Consumo**:
1. Módulo de Estoque envia histórico de vendas (via pedidos entregues) para o engine
2. Módulo de Estoque envia estoque atual (quantidade disponível) para o engine
3. Módulo de Estoque configura parâmetros de reposição (lead time, estoque de segurança)
4. Engine analisa dados e retorna alertas, sugestões e análises
5. Módulo de Estoque apresenta resultados para usuário no contexto de materiais de construção

**Documentação do Engine**: [core-stock-intelligence.md](./core-stock-intelligence.md)

### O Que NÃO Entra no MVP 2

- ❌ Integração automática com fornecedor
- ❌ Previsão avançada (machine learning) - é responsabilidade do engine, não do vertical
- ❌ Otimização de compras (lote econômico)
- ❌ Gestão de múltiplos depósitos

### Próximos Passos (MVP 5+)

- Integração com fornecedor (ordem de compra automática)
- Otimização de compras (lote econômico)
- Gestão de múltiplos depósitos
- Engine pode evoluir com machine learning (independente do vertical)

---

## Módulo 4: Logística e Entrega (MVP 3)

### Objetivo

Reduzir erro, retrabalho e conflito com cliente na entrega, com roteirização simples e prova de entrega.

### Inputs

- Pedidos prontos para entrega
- Endereços das obras
- Motoristas disponíveis
- Veículos disponíveis (futuro)
- Capacidade de carga (futuro)

### Outputs

- Rota de entrega sugerida
- Rota atribuída ao motorista
- Prova de entrega (foto, assinatura)
- Status da entrega atualizado
- Relatório de entregas (tempo, divergências)

### Dependências

- **Módulo 2 (Pedidos)**: Pedidos com status "saiu_entrega"
- **Obras**: Endereços para roteirização
- **Motoristas**: Deve existir motoristas cadastrados
- **Geolocalização**: Endereços devem ter coordenadas (futuro)

### KPIs

- **Tempo médio de entrega**: Reduzir de 3-5 dias para 1-2 dias
- **Taxa de erro na entrega**: Reduzir de ~10% para <3%
- **Taxa de conflito (reclamação)**: Reduzir de ~15% para <5%
- **Eficiência da rota**: Reduzir distância percorrida em 20%

### Funcionalidades Principais

- ✅ Roteirização simples (agrupamento por região)
- ✅ Interface simples para entregador (app mobile ou web)
- ✅ Prova de entrega (foto + assinatura)
- ✅ Status da entrega (saiu, chegou, entregue)
- ✅ Registro de divergências (faltou item, item errado)
- ✅ Observações do motorista

### O Que NÃO Entra no MVP 3

- ❌ Rastreamento GPS em tempo real
- ❌ Otimização de rota com algoritmo complexo
- ❌ Integração com transportadora
- ❌ Gestão de múltiplos veículos

### Próximos Passos (MVP 5+)

- Rastreamento GPS em tempo real
- Otimização de rota com algoritmo (TSP, etc.)
- Integração com transportadora
- Gestão de múltiplos veículos e rotas

---

## Módulo 5: E-commerce B2B (MVP 4)

### Objetivo

Permitir recompra sem atrito para clientes recorrentes, com catálogo personalizado e preços negociados.

### Inputs

- Catálogo de produtos (filtrado por cliente)
- Preços negociados por cliente/obra
- Histórico de pedidos do cliente
- Carrinho do cliente

### Outputs

- Catálogo personalizado por cliente
- Pedido criado pelo cliente
- Confirmação de pedido
- Histórico de pedidos do cliente

### Dependências

- **Módulo 1 (Cotações)**: Base para aprovação e conversão
- **Módulo 2 (Pedidos)**: Base para criação de pedido
- **Clientes**: Deve existir cliente com acesso ao portal
- **Produtos**: Deve existir catálogo de produtos
- **Autenticação**: Cliente B2B precisa fazer login

### KPIs

- **Taxa de adoção do portal**: 50%+ dos clientes B2B usam o portal
- **Taxa de recompra via portal**: 30%+ dos pedidos via portal
- **Tempo de criação de pedido pelo cliente**: Reduzir de 10-15 minutos (via vendedor) para 3-5 minutos (via portal)
- **Satisfação do cliente**: 80%+ satisfeitos com portal

### Funcionalidades Principais

- ✅ Portal B2B (web) para clientes
- ✅ Login de cliente (acesso separado do sistema interno)
- ✅ Catálogo personalizado por cliente (preços negociados)
- ✅ Preços diferenciados por cliente/obra
- ✅ Carrinho de compras
- ✅ Recompra rápida (duplicar pedido anterior)
- ✅ Histórico de pedidos do cliente
- ✅ Checkout simples (criar pedido diretamente)

### O Que NÃO Entra no MVP 4

- ❌ Pagamento online
- ❌ Integração com sistema fiscal
- ❌ Gestão de frotas pelo cliente
- ❌ Portal B2C (consumidor final)

### Próximos Passos (MVP 5+)

- Pagamento online (boleto, cartão, PIX)
- Integração com sistema fiscal (emissão de nota)
- Portal B2C (consumidor final)
- App mobile para clientes

---

## Visão Geral das Fases

### MVP 1: Cotações → Pedidos → Entrega Básica

**Foco**: Eliminar retrabalho na cotação e aumentar taxa de conversão.

**Módulos**:
- ✅ Cotações (criar, editar, enviar, converter)
- ✅ Pedidos (criar, converter, status básico)
- ✅ Entrega (status manual)

**Resultado Esperado**:
- Tempo de cotação: 3 minutos
- Taxa de conversão: 60%+
- Redução de erro: <5%

---

### MVP 2: Gestão de Estoque + Stock Intelligence Engine

**Foco**: Reduzir ruptura e excesso de estoque usando dados reais, com consumo do Stock Intelligence Engine.

**Módulos**:
- ✅ **Stock Intelligence Engine (Core)**: Análise de vendas, alertas, sugestões, análise ABC
- ✅ **Gestão de Estoque (Vertical)**: Gestão física, interface para visualizar alertas/sugestões do engine
- ✅ Alertas (risco de ruptura) - fornecidos pelo engine
- ✅ Relatórios (itens abaixo/acima do ideal) - gerados pelo vertical com dados do engine

**Resultado Esperado**:
- Ruptura: <5%
- Capital parado: <30%
- Acurácia da sugestão: 80%+ (fornecida pelo engine)

---

### MVP 3: Logística e Prova de Entrega

**Foco**: Reduzir erro, retrabalho e conflito na entrega.

**Módulos**:
- ✅ Roteirização (agrupamento por região)
- ✅ App para motorista (ou web mobile)
- ✅ Prova de entrega (foto, assinatura)
- ✅ Rastreamento de status

**Resultado Esperado**:
- Tempo de entrega: 1-2 dias
- Erro na entrega: <3%
- Conflito: <5%

---

### MVP 4: E-commerce B2B

**Foco**: Permitir recompra sem atrito para clientes recorrentes.

**Módulos**:
- ✅ Portal B2B (web)
- ✅ Catálogo personalizado por cliente
- ✅ Preços negociados
- ✅ Recompra rápida
- ✅ Checkout simples

**Resultado Esperado**:
- Adoção do portal: 50%+
- Recompra via portal: 30%+
- Satisfação: 80%+

---

### MVP 5+: Expansão e Integração

**Foco**: Integração com sistemas externos e expansão de funcionalidades.

**Módulos Futuros**:
- Integração fiscal (emissão de nota)
- Pagamento online
- Rastreamento GPS
- Portal B2C
- App mobile para clientes
- Machine learning para previsão

---

## Dependências Entre Módulos

```
MVP 1 (Base)
  ├── Cotações (Vertical)
  ├── Pedidos (Vertical)
  └── Entrega Básica (Vertical)

MVP 2 (Estoque)
  ├── Stock Intelligence Engine (Core) - Novo
  └── Gestão de Estoque (Vertical)
      └── Depende de: MVP 1 (histórico de vendas via pedidos)
      └── Consome: Stock Intelligence Engine

MVP 3 (Logística)
  └── Depende de: MVP 1 (pedidos)

MVP 4 (E-commerce B2B)
  └── Depende de: MVP 1 (cotações e pedidos)

MVP 5+ (Integração)
  └── Depende de: MVP 1-4 (todos os módulos)
  └── Stock Intelligence Engine pode ser consumido por novos verticais
```

---

## Critérios de Sucesso por Módulo

### MVP 1: Cotações

- ✅ 80%+ das cotações criadas em <5 minutos
- ✅ 60%+ das cotações aprovadas são convertidas em pedidos
- ✅ <5% de erro em pedidos criados a partir de cotações
- ✅ 90%+ de satisfação do vendedor

### MVP 2: Gestão de Estoque + Stock Intelligence Engine

**Métricas do Vertical (Gestão de Estoque)**:
- ✅ <5% dos itens em ruptura
- ✅ <30% de capital parado em estoque
- ✅ 70%+ das sugestões do engine são seguidas
- ✅ 80%+ de satisfação dos usuários com o módulo

**Métricas do Core (Stock Intelligence Engine)**:
- ✅ 80%+ de acurácia na sugestão de reposição
- ✅ 90%+ de precisão na detecção de risco de ruptura
- ✅ Análise ABC correta (80%+ de acurácia)
- ✅ Explicações claras (80%+ dos usuários entendem)

### MVP 3: Logística

- ✅ 1-2 dias de tempo médio de entrega
- ✅ <3% de erro na entrega
- ✅ <5% de conflito (reclamação)
- ✅ 100% dos pedidos entregues têm prova de entrega

### MVP 4: E-commerce B2B

- ✅ 50%+ dos clientes B2B usam o portal
- ✅ 30%+ dos pedidos são feitos via portal
- ✅ 3-5 minutos para criar pedido no portal
- ✅ 80%+ de satisfação do cliente

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

