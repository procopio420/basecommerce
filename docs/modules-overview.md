# Visão Geral dos Módulos

## Estrutura Arquitetural

O sistema é composto por dois tipos de módulos:

1. **Core Modules (Horizontais)**: Módulos reutilizáveis que resolvem problemas universais, independentes do vertical de negócio.
2. **Vertical Modules (Materiais de Construção)**: Módulos específicos do vertical de materiais de construção que consomem os core modules.

---

## Core Modules (Horizontais) - Engines

### 1. Stock Intelligence Engine

**Descrição**: Engine horizontal que fornece inteligência de estoque baseada em dados históricos de vendas. Resolve problemas universais de decisão de compra: **O QUE comprar, QUANDO comprar e QUANTO comprar**.

**Documentação**: [core-stock-intelligence.md](./core-stock-intelligence.md)

**Responsabilidade**: Ajudar o negócio a decidir **O QUE comprar, QUANDO comprar e QUANTO comprar**.

**O Que FAZ**:
- ✅ Analisa histórico de vendas
- ✅ Analisa estoque atual
- ✅ Considera lead time de fornecedor
- ✅ Considera sazonalidade (tempo)
- ✅ Classifica produtos (ex: ABC)
- ✅ Gera alertas de risco de ruptura
- ✅ Gera alertas de excesso de estoque
- ✅ Sugere quantidades de reposição
- ✅ Explica o motivo da sugestão (transparência)

**O Que NÃO Faz**:
- ❌ Não compra produtos
- ❌ Não fala com fornecedores
- ❌ Não gera pedidos
- ❌ Não define preço de venda
- ❌ Não conhece regras do setor

**Regra de Ouro**: Apenas **INFORMA e RECOMENDA**. Quem decide e executa é o **Vertical App**.

**Consumido Por**:
- Vertical de Materiais de Construção (atual)
- Futuros verticais (alimentação, eletrônicos, varejo, etc.)

**Status**: MVP 2 (planejado)

---

### 2. Pricing & Supplier Intelligence Engine

**Descrição**: Engine horizontal que fornece inteligência de fornecedor e custo. Resolve problemas universais de decisão de compra: **DE QUEM comprar e A QUE CUSTO**.

**Documentação**: [core-pricing-supplier-intelligence.md](./core-pricing-supplier-intelligence.md)

**Responsabilidade**: Ajudar o negócio a decidir **DE QUEM comprar e A QUE CUSTO**.

**O Que FAZ**:
- ✅ Registra preços de fornecedores por produto
- ✅ Mantém histórico de preços por fornecedor
- ✅ Compara fornecedores (A vs B)
- ✅ Calcula custo médio atualizado
- ✅ Identifica variações relevantes de preço
- ✅ Sugere fornecedor mais vantajoso
- ✅ Expõe "custo base" para outros módulos

**O Que NÃO Faz**:
- ❌ Não executa compra
- ❌ Não negocia automaticamente
- ❌ Não fala com cliente final
- ❌ Não define margem
- ❌ Não gera preço de venda final

**Regra de Ouro**: Apenas **ORGANIZA e COMPARA custos**. Quem decide e executa é o **Vertical App**.

**Consumido Por**:
- Vertical de Materiais de Construção (atual)
- Futuros verticais (alimentação, eletrônicos, varejo, etc.)

**Status**: MVP 2 (planejado)

---

### 3. Delivery & Fulfillment Engine

**Descrição**: Engine horizontal que gerencia o ciclo de entrega. Resolve problemas universais de logística: **pedido → entrega → confirmação**.

**Documentação**: [core-delivery-fulfillment.md](./core-delivery-fulfillment.md)

**Responsabilidade**: Gerenciar o ciclo **pedido → entrega → confirmação**.

**O Que FAZ**:
- ✅ Planeja entregas
- ✅ Agrupa pedidos por rota
- ✅ Controla status da entrega
- ✅ Registra ocorrências
- ✅ Coleta prova de entrega (foto, assinatura)
- ✅ Calcula custo por entrega
- ✅ Retorna dados para análise operacional

**O Que NÃO Faz**:
- ❌ Não vende
- ❌ Não cobra cliente
- ❌ Não define preço do frete
- ❌ Não emite nota
- ❌ Não decide políticas comerciais

**Regra de Ouro**: Apenas **EXECUTA e REGISTRA entregas**. Quem define o que entregar é o **Vertical App**.

**Consumido Por**:
- Vertical de Materiais de Construção (atual)
- Futuros verticais (alimentação, eletrônicos, varejo, etc.)

**Status**: MVP 3 (planejado)

---

### 4. Sales Intelligence Engine

**Descrição**: Engine horizontal que fornece inteligência de vendas. Resolve problemas universais de aumento de valor de venda: **AUMENTAR o valor da venda** com sugestões lógicas.

**Documentação**: [core-sales-intelligence.md](./core-sales-intelligence.md)

**Responsabilidade**: Ajudar o negócio a **AUMENTAR o valor da venda** com sugestões lógicas.

**O Que FAZ**:
- ✅ Sugere produtos complementares
- ✅ Sugere produtos substitutos
- ✅ Identifica padrões de compra
- ✅ Recomenda bundles
- ✅ Usa regras simples (não IA pesada inicialmente)
- ✅ Retorna sugestões explicáveis

**O Que NÃO Faz**:
- ❌ Não cria cotação
- ❌ Não fecha venda
- ❌ Não conversa com cliente
- ❌ Não define preços
- ❌ Não altera pedidos sozinha

**Regra de Ouro**: Apenas **SUGERE oportunidades de venda**. Quem decide e executa é o **Vertical App**.

**Consumido Por**:
- Vertical de Materiais de Construção (atual)
- Futuros verticais (alimentação, eletrônicos, varejo, etc.)

**Status**: MVP 1 (pode ser usado nas cotações) / MVP 4 (recursos avançados)

---

### Princípios das Engines

**Regra de Ouro das Engines**:
- Engines **NÃO têm UI própria**
- Engines **NÃO conhecem o cliente final**
- Engines **NÃO tomam decisões finais**
- Engines **NÃO executam ações comerciais**

**Engines**:
- → Recebem dados
- → Processam
- → Devolvem recomendações

**Quem decide e executa**: **Vertical App**

**Papel do Vertical (Materiais de Construção)**:
- Possui UX
- Possui fluxo de cotação
- Possui pedido
- Possui regras do setor
- **Consome as engines**
- **Decide quando usar ou ignorar sugestões**

**Exemplo de Consumo**:
- Cotação → chama Sales Intelligence Engine
- Compra → consulta Stock Intelligence + Pricing & Supplier Intelligence Engine
- Entrega → usa Delivery & Fulfillment Engine

---

## Vertical Modules (Materiais de Construção)

### 1. Quotations (Cotações)

**Descrição**: Módulo específico para criar cotações rapidamente (3 minutos) e converter em pedidos sem retrabalho. **Pode consumir o Sales Intelligence Engine** para sugerir produtos complementares.

**Documentação**: [04-modules-and-phases.md](./04-modules-and-phases.md#módulo-1-cotações-mvp-1)

**Responsabilidades**:
- ✅ Criar cotação em 3 minutos
- ✅ Buscar cliente e produto em tempo real
- ✅ Aplicar regras simples de preço (tabela base + desconto)
- ✅ Salvar como rascunho ou enviar
- ✅ Histórico de cotações
- ✅ Converter cotação aprovada em pedido (1 clique)
- ✅ **Sugerir produtos complementares** (via Sales Intelligence Engine - futuro)

**Dependências**:
- ✅ Módulo Base (multi-tenant, autenticação, usuários)
- ✅ Client Management (gerenciamento de clientes)
- ✅ Product Catalog (catálogo de produtos)
- ✅ **Sales Intelligence Engine** (sugestões de produtos - futuro)

**Como Pode Consumir o Sales Intelligence Engine**:
- ✅ Envia produtos no carrinho/cotação atual
- ✅ Recebe sugestões de produtos complementares
- ✅ Recebe sugestões de produtos substitutos
- ✅ Recebe recomendações de bundles
- ✅ Apresenta sugestões para vendedor
- ✅ Vendedor decide se adiciona produtos sugeridos

**Status**: MVP 1 (implementado) - Sales Intelligence Engine pode ser integrado em fase futura

---

### 2. Orders (Pedidos)

**Descrição**: Módulo específico para gerenciar pedidos criados a partir de cotações ou diretamente, com rastreamento básico de status.

**Documentação**: [04-modules-and-phases.md](./04-modules-and-phases.md#módulo-2-pedidos-mvp-1---básico)

**Responsabilidades**:
- ✅ Criar pedido direto ou converter de cotação
- ✅ Histórico de pedidos
- ✅ Atualizar status (pendente, em_preparacao, saiu_entrega, entregue, cancelado)
- ✅ Dashboard com pedidos do dia
- ✅ Visualizar detalhes do pedido

**Dependências**:
- ✅ Módulo Base (multi-tenant, autenticação, usuários)
- ✅ Quotations (pedidos podem vir de cotações)
- ✅ Client Management (gerenciamento de clientes)
- ✅ Product Catalog (catálogo de produtos)

**Status**: MVP 1 (implementado)

---

### 3. Stock Management (Gestão de Estoque - Vertical)

**Descrição**: Módulo específico para gerenciar estoque físico do vertical de materiais de construção. **Consome o Stock Intelligence Engine** para obter sugestões e alertas. **Pode consumir o Pricing & Supplier Intelligence Engine** para obter custo base e comparar fornecedores.

**Documentação**: [04-modules-and-phases.md](./04-modules-and-phases.md#módulo-3-estoque-inteligente-mvp-2)

**Responsabilidades**:
- ✅ Gestão de estoque físico (quantidade atual, entradas/saídas)
- ✅ Atualização manual de estoque
- ✅ Interface para visualizar alertas do Stock Intelligence Engine
- ✅ Interface para visualizar sugestões de reposição do Stock Intelligence Engine
- ✅ Relatório de estoque (itens abaixo do mínimo, itens acima do máximo)
- ✅ Integração com pedidos (atualiza estoque quando pedido é entregue)
- ✅ **Visualizar comparação de fornecedores** (via Pricing & Supplier Intelligence Engine)
- ✅ **Visualizar custo base** (via Pricing & Supplier Intelligence Engine)

**Dependências**:
- ✅ Módulo Base (multi-tenant, autenticação, usuários)
- ✅ Product Catalog (catálogo de produtos)
- ✅ Orders (histórico de vendas via pedidos)
- ✅ **Stock Intelligence Engine** (alertas, sugestões, análise ABC)
- ✅ **Pricing & Supplier Intelligence Engine** (comparação de fornecedores, custo base - futuro)

**Como Consome o Stock Intelligence Engine**:
- ✅ Envia histórico de vendas (via pedidos entregues)
- ✅ Envia estoque atual (quantidade disponível)
- ✅ Configura parâmetros de reposição (lead time, estoque de segurança)
- ✅ Recebe alertas de risco de ruptura
- ✅ Recebe sugestões de reposição (O QUE comprar, QUANDO, QUANTO)
- ✅ Recebe análise ABC

**Como Pode Consumir o Pricing & Supplier Intelligence Engine**:
- ✅ Recebe comparação de fornecedores para produto específico
- ✅ Recebe sugestão de fornecedor mais vantajoso
- ✅ Recebe custo base (para calcular valor de estoque)
- ✅ Recebe alertas de variação de preço
- ✅ Decide qual fornecedor usar (pode seguir ou ignorar sugestão)

**Status**: MVP 2 (planejado)

---

### 4. Logistics (Logística)

**Descrição**: Módulo específico para gerenciar entregas de pedidos em obras, com roteirização simples e prova de entrega. **Consome o Delivery & Fulfillment Engine** para obter rotas e controlar entregas.

**Documentação**: [04-modules-and-phases.md](./04-modules-and-phases.md#módulo-4-logística-e-entrega-mvp-3)

**Responsabilidades**:
- ✅ Interface para planejar entregas
- ✅ Interface simples para entregador (app mobile ou web)
- ✅ Visualizar rotas sugeridas pelo Delivery & Fulfillment Engine
- ✅ Atribuir motorista para rota
- ✅ Visualizar status da entrega (fornecido pelo engine)
- ✅ Visualizar prova de entrega (coletada pelo engine)
- ✅ Registrar divergências (fornecido pelo engine)

**Dependências**:
- ✅ Módulo Base (multi-tenant, autenticação, usuários)
- ✅ Orders (pedidos com status "saiu_entrega")
- ✅ Client Management (endereços das obras)
- ✅ Works (obras com endereços para roteirização)
- ✅ **Delivery & Fulfillment Engine** (rotas, status, prova de entrega)

**Como Consome o Delivery & Fulfillment Engine**:
- ✅ Envia pedidos prontos para entrega
- ✅ Solicita planejamento de rotas
- ✅ Recebe rotas sugeridas (agrupamento por região)
- ✅ Atribui motorista para rota
- ✅ Recebe atualizações de status da entrega
- ✅ Recebe prova de entrega (foto, assinatura)
- ✅ Recebe ocorrências registradas

**Status**: MVP 3 (planejado)

---

### 5. B2B Commerce (E-commerce B2B)

**Descrição**: Módulo específico para permitir recompra sem atrito para clientes recorrentes, com catálogo personalizado e preços negociados.

**Documentação**: [04-modules-and-phases.md](./04-modules-and-phases.md#módulo-5-e-commerce-b2b-mvp-4)

**Responsabilidades**:
- ✅ Portal B2B (web) para clientes
- ✅ Login de cliente (acesso separado do sistema interno)
- ✅ Catálogo personalizado por cliente (preços negociados)
- ✅ Preços diferenciados por cliente/obra
- ✅ Carrinho de compras
- ✅ Recompra rápida (duplicar pedido anterior)
- ✅ Histórico de pedidos do cliente
- ✅ Checkout simples (criar pedido diretamente)

**Dependências**:
- ✅ Módulo Base (multi-tenant, autenticação, usuários)
- ✅ Quotations (base para aprovação e conversão)
- ✅ Orders (base para criação de pedido)
- ✅ Client Management (clientes com acesso ao portal)
- ✅ Product Catalog (catálogo de produtos)

**Status**: MVP 4 (planejado)

---

## Módulo Base (Fundação)

### Base Platform

**Descrição**: Fundação do sistema que suporta todos os módulos (core e vertical).

**Responsabilidades**:
- ✅ Multi-tenant (isolamento de dados por loja)
- ✅ Autenticação e autorização (JWT, roles)
- ✅ Gerenciamento de usuários
- ✅ Infraestrutura compartilhada (banco de dados, APIs, etc.)

**Consumido Por**: Todos os módulos (core e vertical)

**Status**: MVP 1 (implementado)

---

## Diagrama Arquitetural

```
┌─────────────────────────────────────────────────────────┐
│           Base Platform (Fundação)                     │
│  - Multi-tenant                                         │
│  - Autenticação                                         │
│  - Usuários                                             │
└─────────────────────────────────────────────────────────┘
           ▲                    ▲
           │                    │
┌──────────┴─────────┐  ┌──────┴──────────────────┐
│  Core Engines      │  │  Vertical Modules       │
│  (Horizontais)     │  │  (Materiais Construção) │
├────────────────────┤  ├─────────────────────────┤
│                    │  │                         │
│  1. Stock          │  │  Quotations ──┐         │
│     Intelligence   │  │  (Sales Engine)│        │
│     Engine         │◄─┼──┤             │        │
│                    │  │  Orders       │        │
│  2. Pricing &      │  │               │        │
│     Supplier       │◄─┼── Stock Mgmt ─┤        │
│     Intelligence   │  │  (Stock +     │        │
│     Engine         │  │   Pricing)    │        │
│                    │  │               │        │
│  3. Delivery &     │◄─┼── Logistics ──┤        │
│     Fulfillment    │  │               │        │
│     Engine         │  │  B2B Commerce │        │
│                    │  │                         │
│  4. Sales          │◄─┼──┤                      │
│     Intelligence   │  │  └─────────────────────┘
│     Engine         │  │
└────────────────────┘  └─────────────────────────┘

Regra de Ouro:
Engines → recebem dados → processam → devolvem recomendações
Vertical → decide → executa
```

---

## Princípios de Design

### 1. Separação Core vs Vertical

- **Core modules** resolvem problemas universais e são reutilizáveis
- **Vertical modules** resolvem problemas específicos do vertical e consomem core modules
- **Não misturar**: Lógica específica de vertical não entra em core module

### 2. Consumo Via API Genérica

- Core modules expõem APIs genéricas (não específicas de vertical)
- Vertical modules consomem APIs genéricas e interpretam para seu contexto
- Interface genérica permite evolução independente

### 3. Evolução Independente

- Core modules podem evoluir sem afetar vertical modules
- Vertical modules podem evoluir sem afetar core modules
- Novos verticais podem consumir core modules sem modificá-los

### 4. Isolamento de Responsabilidades

- **Core module**: Inteligência (o que fazer, por quê)
- **Vertical module**: Execução (como fazer, quando fazer)

### 5. Validação Antes de Criar Core Module

- Core module só é criado quando há necessidade comprovada de reutilização
- Não antecipar criação de core modules sem validação
- Priorizar vertical inicial antes de criar novos core modules

---

## Estratégia de Expansão

### Fase 1: Vertical Inicial (Materiais de Construção)

- ✅ Implementar vertical modules (Quotations, Orders, etc.)
- ✅ Criar Stock Intelligence Engine quando necessário (MVP 2)
- ✅ Validar engine com vertical inicial

### Fase 2: Refinamento do Core Module

- ✅ Refinar Stock Intelligence Engine baseado em feedback do vertical inicial
- ✅ Estabilizar APIs genéricas
- ✅ Documentar consumo do engine

### Fase 3: Expansão para Novos Verticais

- ✅ Oferecer Stock Intelligence Engine para outros verticais
- ✅ Novos verticais consomem engine sem modificá-lo
- ✅ Engine evolui baseado em necessidades de múltiplos verticais

### Fase 4: Novos Core Modules (Se Necessário)

- ✅ Criar novos core modules apenas quando há necessidade comprovada de reutilização
- ✅ Validar necessidade antes de criar
- ✅ Não antecipar criação sem validação

---

## Dependências Entre Módulos

### Vertical Modules Dependem de Core Modules

| Vertical Module | Core Module | Como Consome |
|----------------|-------------|--------------|
| Quotations | Sales Intelligence Engine | Envia produtos no carrinho, recebe sugestões de produtos complementares/substitutos/bundles |
| Stock Management | Stock Intelligence Engine | Envia vendas/estoque, recebe alertas/sugestões (O QUE/QUANDO/QUANTO comprar) |
| Stock Management | Pricing & Supplier Intelligence Engine | Recebe comparação de fornecedores, custo base, sugestão de fornecedor |
| Logistics | Delivery & Fulfillment Engine | Envia pedidos prontos, recebe rotas, status, prova de entrega |

### Vertical Modules Dependem de Outros Vertical Modules

| Módulo | Depende De | Relação |
|--------|------------|---------|
| Orders | Quotations | Pedidos podem vir de cotações |
| Stock Management | Orders | Histórico de vendas via pedidos |
| Logistics | Orders | Pedidos com status "saiu_entrega" |
| B2B Commerce | Quotations, Orders | Base para aprovação e criação de pedido |

---

## Observações Importantes

### 1. Engines São Horizontais, Não Verticais

Engines não sabem que "cimento" é diferente de "leite". Eles apenas analisam:
- **Stock Intelligence**: Identificador de produto, quantidade vendida, período, lead time
- **Pricing & Supplier Intelligence**: Identificador de produto, fornecedor, preço, data
- **Delivery & Fulfillment**: Identificador de pedido, endereço, produtos, status
- **Sales Intelligence**: Identificador de produto, padrões de compra, frequência

### 2. Vertical Interpreta Outputs

O vertical decide como apresentar sugestões para usuário:
- **Stock Intelligence**: "Comprar cimento para obra X" (materiais) vs "Comprar leite para reposição diária" (alimentação)
- **Pricing & Supplier Intelligence**: "Fornecedor B: R$ 30 para cimento" (materiais) vs "Fornecedor Y: R$ 5,30 para leite" (alimentação)
- **Delivery & Fulfillment**: "Rota para obras: Obra A, Obra B" (materiais) vs "Rota residencial: Bairro A, Bairro B" (alimentação)
- **Sales Intelligence**: "Também recomendamos: Brita (80% compram junto)" (materiais) vs "Também recomendamos: Café (75% compram junto)" (alimentação)

### 3. Engines Não Conhecem Vertical

Engines não têm conhecimento sobre o vertical. Eles apenas fornecem inteligência genérica.

### 4. Vertical Module Consome Engines

Vertical modules consomem engines via APIs genéricas e interpretam para seu contexto específico.

### 5. Regra de Ouro das Engines

- Engines **NÃO têm UI própria**
- Engines **NÃO conhecem o cliente final**
- Engines **NÃO tomam decisões finais**
- Engines **NÃO executam ações comerciais**

Engines apenas: **recebem dados → processam → devolvem recomendações**

Vertical decide e executa.

---

## Métricas de Sucesso

### Core Engines

**Stock Intelligence Engine**:
- ✅ **Reutilização**: 2+ verticais usando o engine em 12 meses
- ✅ **Acurácia**: 80%+ de acurácia na sugestão de reposição (O QUE/QUANDO/QUANTO)
- ✅ **Adoção**: 70%+ dos clientes do vertical inicial adotam o módulo
- ✅ **Satisfação**: 80%+ de satisfação dos usuários

**Pricing & Supplier Intelligence Engine**:
- ✅ **Reutilização**: 2+ verticais usando o engine em 12 meses
- ✅ **Acurácia**: 90%+ de precisão na comparação de fornecedores
- ✅ **Adoção**: 70%+ dos clientes do vertical inicial adotam o módulo
- ✅ **Resultado**: Redução de 10%+ no custo de compra

**Delivery & Fulfillment Engine**:
- ✅ **Reutilização**: 2+ verticais usando o engine em 12 meses
- ✅ **Eficiência**: Redução de 15%+ na distância percorrida (roteirização)
- ✅ **Adoção**: 80%+ dos clientes do vertical inicial adotam o módulo
- ✅ **Resultado**: Taxa de sucesso de entrega >95%

**Sales Intelligence Engine**:
- ✅ **Reutilização**: 2+ verticais usando o engine em 12 meses
- ✅ **Efetividade**: Aumento de 15%+ no ticket médio (vendas complementares)
- ✅ **Adoção**: 60%+ dos clientes do vertical inicial adotam sugestões
- ✅ **Resultado**: Taxa de conversão de sugestões >20%

### Vertical Modules

**Stock Management**:
- ✅ **Integração**: Consumo transparente do engine (usuário não vê diferença)
- ✅ **Adoção**: 70%+ dos clientes adotam o módulo de estoque
- ✅ **Resultado**: Redução de ruptura para <5%, redução de capital parado para <30%

**Logistics**:
- ✅ **Integração**: Consumo transparente do Delivery & Fulfillment Engine
- ✅ **Adoção**: 80%+ dos clientes adotam o módulo de logística
- ✅ **Resultado**: Taxa de sucesso de entrega >95%, redução de 15%+ no tempo de entrega

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

