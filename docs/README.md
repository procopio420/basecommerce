# Documentação do Sistema

## Estrutura da Documentação

Esta documentação é a base do sistema e deve ser lida antes de qualquer implementação de código. Cada arquivo é autossuficiente e cobre um aspecto específico do produto.

### 📋 Documentos Principais

1. **[00-product-vision.md](./00-product-vision.md)**
   - Visão do produto
   - Problema que resolve
   - Para quem é
   - O que NÃO é
   - Diferencial competitivo
   - Métricas de sucesso

2. **[01-domain-model.md](./01-domain-model.md)**
   - Entidades principais
   - Responsabilidade de cada entidade
   - Relações entre entidades
   - O que é núcleo vs módulo futuro

3. **[02-user-roles.md](./02-user-roles.md)**
   - Papéis de usuário (Admin, Vendedor, Financeiro, etc.)
   - O que cada um faz
   - O que cada um NÃO pode fazer
   - Permissões e matriz de acesso

4. **[03-core-flows.md](./03-core-flows.md)**
   - Fluxo de cotação (passo a passo)
   - Fluxo de conversão em pedido
   - Fluxo de entrega
   - Fluxo de recompra
   - Fluxo de reposição de estoque

5. **[04-modules-and-phases.md](./04-modules-and-phases.md)**
   - Módulo 1: Cotações (MVP 1)
   - Módulo 2: Pedidos (MVP 1)
   - Módulo 3: Gestão de Estoque (MVP 2)
   - Módulo 4: Logística (MVP 3)
   - Módulo 5: E-commerce B2B (MVP 4)
   - Objetivos, inputs, outputs, dependências, KPIs

6. **[modules-overview.md](./modules-overview.md)**
   - Visão geral da arquitetura modular
   - Core Modules (horizontais, reutilizáveis)
   - Vertical Modules (materiais de construção)
   - Separação de responsabilidades
   - Estratégia de expansão

7. **[modules-overview.md](./modules-overview.md)**
   - Visão geral da arquitetura modular
   - Core Engines (horizontais, reutilizáveis)
   - Vertical Modules (materiais de construção)
   - Separação de responsabilidades
   - Estratégia de expansão

8. **[core-stock-intelligence.md](./core-stock-intelligence.md)**
   - Stock Intelligence Engine (módulo horizontal)
   - Responsabilidade: O QUE/QUANDO/QUANTO comprar
   - O que faz e o que NÃO faz
   - Inputs e outputs genéricos
   - Como é consumido por verticais
   - Limites de responsabilidade

9. **[core-pricing-supplier-intelligence.md](./core-pricing-supplier-intelligence.md)**
   - Pricing & Supplier Intelligence Engine (módulo horizontal)
   - Responsabilidade: DE QUEM comprar e A QUE CUSTO
   - O que faz e o que NÃO faz
   - Inputs e outputs genéricos
   - Como é consumido por verticais
   - Limites de responsabilidade

10. **[core-delivery-fulfillment.md](./core-delivery-fulfillment.md)**
    - Delivery & Fulfillment Engine (módulo horizontal)
    - Responsabilidade: pedido → entrega → confirmação
    - O que faz e o que NÃO faz
    - Inputs e outputs genéricos
    - Como é consumido por verticais
    - Limites de responsabilidade

11. **[core-sales-intelligence.md](./core-sales-intelligence.md)**
    - Sales Intelligence Engine (módulo horizontal)
    - Responsabilidade: AUMENTAR o valor da venda
    - O que faz e o que NÃO faz
    - Inputs e outputs genéricos
    - Como é consumido por verticais
    - Limites de responsabilidade

8. **[05-non-goals.md](./05-non-goals.md)**
   - O que NÃO será feito
   - O que não é prioridade
   - O que só entra após validação
   - O que nunca será objetivo

9. **[06-assumptions-and-risks.md](./06-assumptions-and-risks.md)**
   - Assunções do negócio
   - Riscos técnicos
   - Riscos de adoção
   - Riscos regionais (Brasil)
   - Mitigações

10. **[07-success-metrics.md](./07-success-metrics.md)**
   - Métricas de produto
   - Métricas de operação
   - Métricas financeiras
   - Métricas de adoção
   - Métricas de retenção

---

## 🗺️ Mapa de Leitura

### Ordem Recomendada por Perfil

#### Para Desenvolvedores (Ordem de Leitura)

1. **Visão Geral**: [`00-product-vision.md`](./00-product-vision.md) - Entenda o problema e o produto
2. **Arquitetura**: [`modules-overview.md`](./modules-overview.md) - Core Engines vs Vertical Modules
3. **Modelo de Domínio**: [`01-domain-model.md`](./01-domain-model.md) - Entidades e relações
4. **Modelo Técnico**: [`../backend/docs/domain-model.md`](../backend/docs/domain-model.md) - Implementação técnica
5. **Fluxos**: [`03-core-flows.md`](./03-core-flows.md) - Como o sistema funciona
6. **Usuários**: [`02-user-roles.md`](./02-user-roles.md) - Papéis e permissões
7. **Engines** (conforme área de trabalho):
   - [`core-stock-intelligence.md`](./core-stock-intelligence.md) - Estoque
   - [`core-pricing-supplier-intelligence.md`](./core-pricing-supplier-intelligence.md) - Fornecedores
   - [`core-delivery-fulfillment.md`](./core-delivery-fulfillment.md) - Logística
   - [`core-sales-intelligence.md`](./core-sales-intelligence.md) - Vendas
8. **Plataforma**: [`platform-overview.md`](./platform-overview.md) - Arquitetura de eventos
9. **Contratos**: [`event-contracts.md`](./event-contracts.md) e [`engine-contracts.md`](./engine-contracts.md)
10. **Histórico**: [`../backend/docs/CHANGELOG.md`](../backend/docs/CHANGELOG.md) - Histórico de implementação

#### Para Product Managers (Ordem de Leitura)

1. **Visão do Produto**: [`00-product-vision.md`](./00-product-vision.md)
2. **Arquitetura Modular**: [`modules-overview.md`](./modules-overview.md)
3. **Domínio**: [`01-domain-model.md`](./01-domain-model.md)
4. **Usuários**: [`02-user-roles.md`](./02-user-roles.md)
5. **Fluxos**: [`03-core-flows.md`](./03-core-flows.md)
6. **Módulos e Fases**: [`04-modules-and-phases.md`](./04-modules-and-phases.md)
7. **Engines** (se relevante):
   - [`core-stock-intelligence.md`](./core-stock-intelligence.md)
   - [`core-pricing-supplier-intelligence.md`](./core-pricing-supplier-intelligence.md)
   - [`core-delivery-fulfillment.md`](./core-delivery-fulfillment.md)
   - [`core-sales-intelligence.md`](./core-sales-intelligence.md)
8. **Não-Objetivos**: [`05-non-goals.md`](./05-non-goals.md)
9. **Métricas**: [`07-success-metrics.md`](./07-success-metrics.md)
10. **Histórico**: [`../backend/docs/CHANGELOG.md`](../backend/docs/CHANGELOG.md)

#### Para Stakeholders (Ordem de Leitura)

1. **Visão do Produto**: [`00-product-vision.md`](./00-product-vision.md)
2. **Módulos e Fases**: [`04-modules-and-phases.md`](./04-modules-and-phases.md)
3. **Não-Objetivos**: [`05-non-goals.md`](./05-non-goals.md)
4. **Riscos**: [`06-assumptions-and-risks.md`](./06-assumptions-and-risks.md)
5. **Métricas**: [`07-success-metrics.md`](./07-success-metrics.md)

---

## Como Usar Esta Documentação

### Para Desenvolvedores

1. **Leia primeiro**: `00-product-vision.md` e `01-domain-model.md`
2. **Entenda a arquitetura**: `modules-overview.md` (Core Engines vs Vertical Modules)
3. **Entenda as engines** (se trabalhar com cada área):
   - `core-stock-intelligence.md` (estoque: O QUE/QUANDO/QUANTO comprar)
   - `core-pricing-supplier-intelligence.md` (fornecedores: DE QUEM comprar e A QUE CUSTO)
   - `core-delivery-fulfillment.md` (logística: pedido → entrega → confirmação)
   - `core-sales-intelligence.md` (vendas: aumentar valor da venda)
4. **Entenda os usuários**: `02-user-roles.md`
5. **Compreenda os fluxos**: `03-core-flows.md`
6. **Conheça os módulos**: `04-modules-and-phases.md`
7. **Saiba o que não fazer**: `05-non-goals.md`
8. **Entenda os riscos**: `06-assumptions-and-risks.md`
9. **Conheça as métricas**: `07-success-metrics.md`

### Para Product Managers

1. **Visão do produto**: `00-product-vision.md`
2. **Arquitetura modular**: `modules-overview.md` (Core Engines vs Vertical Modules)
3. **Domínio**: `01-domain-model.md`
4. **Usuários**: `02-user-roles.md`
5. **Módulos e fases**: `04-modules-and-phases.md`
6. **Engines** (se relevante):
   - `core-stock-intelligence.md`
   - `core-pricing-supplier-intelligence.md`
   - `core-delivery-fulfillment.md`
   - `core-sales-intelligence.md`
7. **Não-objetivos**: `05-non-goals.md`
8. **Métricas**: `07-success-metrics.md`

### Para Stakeholders

1. **Visão do produto**: `00-product-vision.md`
2. **Módulos e fases**: `04-modules-and-phases.md`
3. **Não-objetivos**: `05-non-goals.md`
4. **Riscos**: `06-assumptions-and-risks.md`
5. **Métricas**: `07-success-metrics.md`

---

## Princípios da Documentação

### 1. Autossuficiente

Cada arquivo pode ser lido independentemente e contém toda a informação necessária.

### 2. Clara e Direta

Linguagem clara, sem jargões desnecessários. Pensando em quem vai manter o sistema por 10 anos.

### 3. Arquitetura Modular: Core Engines + Vertical Modules

**Core Engines (Horizontais)**: Engines reutilizáveis que resolvem problemas universais, independentes do vertical de negócio.

**Regra de Ouro das Engines**:
- Engines **NÃO têm UI própria**
- Engines **NÃO conhecem o cliente final**
- Engines **NÃO tomam decisões finais**
- Engines **NÃO executam ações comerciais**

Engines apenas: **recebem dados → processam → devolvem recomendações**

**Vertical Modules**: Módulos específicos do vertical de materiais de construção que consomem os core engines e decidem quando usar ou ignorar sugestões.

**Exemplo**: Stock Intelligence Engine (core) fornece inteligência genérica sobre **O QUE/QUANDO/QUANTO comprar**, enquanto módulo de Gestão de Estoque (vertical) consome o engine, apresenta resultados no contexto de materiais de construção e decide se segue ou ignora as sugestões.

**4 Engines Principais**:
1. **Stock Intelligence**: O QUE comprar, QUANDO comprar, QUANTO comprar
2. **Pricing & Supplier Intelligence**: DE QUEM comprar, A QUE CUSTO
3. **Delivery & Fulfillment**: pedido → entrega → confirmação
4. **Sales Intelligence**: AUMENTAR o valor da venda com sugestões

### 4. Baseada em Problemas Reais

Toda funcionalidade resolve um problema real identificado em lojas de materiais de construção.

### 5. Focada em Valor

Cada módulo e funcionalidade deve gerar valor mensurável para o cliente. Core modules geram valor por reutilização, vertical modules geram valor direto para o cliente.

### 6. Iterativa

Documentação evolui conforme aprendemos com clientes e validamos assunções. Core engines evoluem baseado em múltiplos verticais, vertical modules evoluem baseado em feedback do vertical específico.

### 7. Isolamento de Responsabilidades

**Engines**: Inteligência (o que fazer, por quê) - **NÃO decidem, apenas sugerem**

**Vertical**: Execução (como fazer, quando fazer) - **Decide e executa**

---

## 📚 Documentação Adicional

### Histórico de Implementação

Para ver o histórico completo de implementação, consulte:
- [`../backend/docs/CHANGELOG.md`](../backend/docs/CHANGELOG.md) - Changelog consolidado com todas as fases

### Documentação Técnica

- [`../backend/docs/domain-model.md`](../backend/docs/domain-model.md) - Modelo de domínio implementado

---

## Versão

**Versão atual**: 2.4 (Plataforma Foundations)

**Última atualização**: Janeiro 2026

---

## Contribuindo

Ao adicionar ou modificar funcionalidades:

1. **Atualize a documentação primeiro**
2. **Valide assunções antes de implementar**
3. **Mantenha métricas atualizadas**
4. **Revise não-objetivos se necessário**

---

**Documentação base concluída. Pronto para iniciar implementação.**

