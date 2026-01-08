# Architecture Overview - MVP 2

## Visão Geral

Este documento descreve a arquitetura geral do sistema, incluindo a integração entre os **Horizontal Engines** (engines horizontais reutilizáveis) e o **Vertical App** (Materiais de Construção).

---

## Princípios Arquiteturais

### 1. Horizontal Engines + Vertical Apps

**Engines Horizontais**: Módulos reutilizáveis com responsabilidade limitada e clara. Não conhecem regras específicas do setor.

**Vertical Apps**: Aplicações específicas de negócio que consomem engines. Interpretam outputs no contexto do setor.

### 2. Separação de Responsabilidades

- **Engines**: Apenas informam, recomendam, organizam e executam. **NÃO decidem**.
- **Vertical**: Decide, executa ações comerciais e interpreta no contexto do setor.

### 3. Contratos Claros

- Inputs e outputs são genéricos e bem definidos
- Interfaces são estáveis e backward compatible
- Engines podem evoluir sem afetar vertical

### 4. Integração Bidirecional

- Vertical alimenta engines com dados (eventos, histórico)
- Engines retornam outputs (sugestões, alertas, análises)
- Feedback loop permite melhoria contínua (futuro)

---

## Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                  (React Frontend)                            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│              (Vertical: Materiais Construção)                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services (CotacaoService, PedidoService, etc.)     │  │
│  │  - Orquestra casos de uso                           │  │
│  │  - Consome engines                                  │  │
│  │  - Implementa regras de negócio do vertical         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Domain Layer (Entities, Validators, Exceptions)     │  │
│  │  - Regras de negócio puras do vertical               │  │
│  │  - Não depende de engines                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Consome via Ports/Interfaces
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Horizontal Engines Layer                      │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ Stock          │  │ Pricing &      │  │ Delivery &   │ │
│  │ Intelligence   │  │ Supplier       │  │ Fulfillment  │ │
│  │ Engine         │  │ Intelligence   │  │ Engine       │ │
│  │                │  │ Engine         │  │              │ │
│  │ - Sugestões    │  │ - Comparação   │  │ - Rotas      │ │
│  │ - Alertas      │  │ - Custo base   │  │ - Status     │ │
│  │ - Análise ABC  │  │ - Tendências   │  │ - Prova      │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────┐                                         │
│  │ Sales          │                                         │
│  │ Intelligence   │                                         │
│  │ Engine         │                                         │
│  │                │                                         │
│  │ - Complementar │                                         │
│  │ - Substitutos  │                                         │
│  │ - Bundles      │                                         │
│  └────────────────┘                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Persiste dados
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Layer                            │
│                  (PostgreSQL)                                │
│  - Multi-tenant por tenant_id                                │
│  - Dados do vertical + engines                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Horizontal Engines

### 1. Stock Intelligence Engine

**Responsabilidade**: Ajudar a decidir **O QUE comprar, QUANDO comprar e QUANTO comprar**.

**Inputs principais**:
- Histórico de vendas (pedidos entregues)
- Estoque atual
- Parâmetros de reposição (lead time, estoque de segurança)

**Outputs principais**:
- Alertas de risco de ruptura
- Sugestões de reposição
- Análise ABC

**Consumo pelo Vertical**:
- Dashboard: Exibe alertas de risco
- Gestão de estoque: Visualiza sugestões de reposição
- Compra: Consulta sugestões antes de criar pedido de compra

**Eventos que Vertical envia**:
- Pedido entregue → Histórico de vendas
- Estoque atualizado → Estoque atual
- Parâmetros configurados → Configurações de reposição

---

### 2. Pricing & Supplier Intelligence Engine

**Responsabilidade**: Ajudar a decidir **DE QUEM comprar e A QUE CUSTO**.

**Inputs principais**:
- Preços de fornecedores por produto
- Histórico de preços

**Outputs principais**:
- Comparação de fornecedores
- Custo base (preço recomendado)
- Alertas de variação de preço
- Tendências de preço

**Consumo pelo Vertical**:
- Gestão de fornecedores: Compara preços
- Cotação de compra: Consulta custo base
- Negociação: Visualiza histórico e tendências

**Eventos que Vertical envia**:
- Preço de fornecedor registrado → Histórico de preços
- Preço atualizado → Detecção de variação
- Pedido de compra criado → Feedback de escolha (futuro)

**Integração com outros engines**:
- Stock Intelligence: Consome custo base para calcular valor de estoque
- Sales Intelligence: Pode consumir custo base para sugerir margem (futuro)

---

### 3. Delivery & Fulfillment Engine

**Responsabilidade**: Gerenciar ciclo **pedido → entrega → confirmação**.

**Inputs principais**:
- Pedidos prontos para entrega
- Endereços de entrega
- Motoristas disponíveis

**Outputs principais**:
- Rotas sugeridas (agrupamento por região)
- Status de entrega atualizado
- Prova de entrega (foto, assinatura)
- Custo de entrega

**Consumo pelo Vertical**:
- Gestão de entregas: Planeja rotas
- Rastreamento: Atualiza status em tempo real
- Confirmação: Registra prova de entrega

**Eventos que Vertical envia**:
- Pedido pronto para entrega → Planejamento de rotas
- Status atualizado → Rastreamento
- Prova de entrega → Confirmação
- Entrega finalizada → Feed para Stock Intelligence

**Integração com outros engines**:
- Stock Intelligence: Recebe dados de entrega finalizada (pedido entregue = venda concluída)

---

### 4. Sales Intelligence Engine

**Responsabilidade**: Ajudar a **AUMENTAR o valor da venda** com sugestões lógicas.

**Inputs principais**:
- Histórico de vendas (produtos vendidos juntos)
- Contexto atual (produtos no carrinho/cotação)
- Catálogo de produtos

**Outputs principais**:
- Sugestões de produtos complementares
- Sugestões de produtos substitutos
- Recomendações de bundles
- Padrões de compra identificados

**Consumo pelo Vertical**:
- Criação de cotação: Exibe sugestões durante criação
- Produto indisponível: Sugere substitutos
- Finalização: Sugere produtos adicionais

**Eventos que Vertical envia**:
- Venda concluída → Histórico de vendas
- Contexto de criação → Solicitação de sugestões
- Sugestão seguida/ignorada → Feedback (futuro)

**Integração com outros engines**:
- Stock Intelligence: Pode consultar disponibilidade (futuro)
- Pricing: Pode usar custo base para sugerir margem (futuro)

---

## Fluxo de Integração Vertical ↔ Engines

### Fluxo 1: Criação de Cotação com Sugestões

```
1. Vendedor cria cotação e adiciona "Cimento"
   ↓
2. CotacaoService adiciona produto à cotação
   ↓
3. CotacaoService consulta Sales Intelligence Engine
   POST /sales-intelligence/v1/suggestions
   { produtos: ["cimento"] }
   ↓
4. Sales Intelligence retorna: ["Areia", "Brita"]
   ↓
5. Vertical exibe sugestões no contexto de materiais de construção
   ↓
6. Vendedor decide adicionar "Areia"
   ↓
7. Vertical atualiza cotação e consulta novamente
   ↓
8. Sales Intelligence retorna: ["Brita"] (70% compram os 3 juntos)
   ↓
9. Vendedor finaliza cotação (com ou sem sugestões)
   ↓
10. Quando cotação é convertida em pedido:
    Vertical envia evento "venda_concluida" para Sales Intelligence
```

### Fluxo 2: Pedido Entregue Alimenta Stock Intelligence

```
1. Pedido é marcado como "pronto para entrega"
   ↓
2. PedidoService atualiza status do pedido
   ↓
3. PedidoService consulta Delivery Engine
   POST /delivery-fulfillment/v1/routes/plan
   { pedidos: [...] }
   ↓
4. Delivery Engine retorna rotas sugeridas
   ↓
5. Usuário atribui motorista e entrega é executada
   ↓
6. Motorista registra prova de entrega
   ↓
7. Delivery Engine confirma entrega finalizada
   ↓
8. PedidoService atualiza status do pedido para "entregue"
   ↓
9. PedidoService envia evento "pedido_entregue" para Stock Intelligence
   { produto_id, quantidade, data_entrega }
   ↓
10. Stock Intelligence atualiza histórico de vendas
    ↓
11. Stock Intelligence recalcula sugestões de reposição
    ↓
12. Próxima consulta retorna sugestões atualizadas
```

### Fluxo 3: Compra de Reposição com Sugestões

```
1. Usuário visualiza dashboard e vê alerta de risco de ruptura
   "Cimento: Risco alto, ruptura em 5 dias"
   ↓
2. Usuário clica em "Ver sugestões de reposição"
   ↓
3. Vertical consulta Stock Intelligence Engine
   GET /stock-intelligence/v1/suggestions?product_id=cimento
   ↓
4. Stock Intelligence retorna:
   { quantidade_sugerida: 100, estoque_minimo: 50, estoque_maximo: 150 }
   ↓
5. Vertical consulta Pricing Engine para obter custo base
   GET /pricing-supplier/v1/base-cost?product_id=cimento
   ↓
6. Pricing Engine retorna:
   { custo_base: 30.00, fornecedor_recomendado: "Fornecedor A" }
   ↓
7. Vertical exibe sugestão no contexto de materiais de construção:
   "Sugestão: Comprar 100 sacos de Cimento por R$ 30,00 (Fornecedor A)"
   ↓
8. Usuário decide criar pedido de compra (seguindo ou ajustando sugestão)
   ↓
9. Vertical cria pedido de compra
   ↓
10. Vertical envia evento "sugestao_seguida" para Stock Intelligence (feedback)
    ↓
11. Quando produto é recebido:
    Vertical envia evento "estoque_atualizado" para Stock Intelligence
```

---

## Diagrama de Comunicação entre Engines

```
┌─────────────────────────────────────────────────────────────┐
│                  Vertical: Materiais Construção              │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Cotacao  │  │ Pedido   │  │ Estoque  │  │Fornecedor│   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │           │
│       │             │             │             │           │
│       │             │             │             │           │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Horizontal Engines                        │
│                                                              │
│  ┌──────────────────┐                                       │
│  │ Sales            │  ← Sugestões durante criação          │
│  │ Intelligence     │  ← Venda concluída (feedback)         │
│  └──────────────────┘                                       │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ Stock            │ ←──────→│ Pricing &        │         │
│  │ Intelligence     │         │ Supplier         │         │
│  │                  │         │ Intelligence     │         │
│  │ ← Vendas         │         │                  │         │
│  │ ← Estoque        │         │ ← Preços         │         │
│  │ → Sugestões      │         │ → Custo base     │         │
│  └──────────────────┘         └──────────────────┘         │
│         ▲                            │                      │
│         │                            │                      │
│         │                            │                      │
│         └────────────────────────────┘                      │
│                  Custo base para valor estoque              │
│                                                              │
│  ┌──────────────────┐                                       │
│  │ Delivery &       │                                       │
│  │ Fulfillment      │                                       │
│  │                  │                                       │
│  │ ← Pedidos        │                                       │
│  │ → Rotas          │                                       │
│  │ → Status         │                                       │
│  │ → Prova          │                                       │
│  └────────┬─────────┘                                       │
│           │                                                  │
│           │ Entrega finalizada                               │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ Stock            │  ← Alimenta histórico de vendas       │
│  │ Intelligence     │                                       │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Contratos de Integração

### 1. Ports e Adapters Pattern

**Abstração**: Cada engine expõe uma interface (Port) que o vertical implementa (Adapter).

**Exemplo - Stock Intelligence Port**:
```python
class StockIntelligencePort:
    def get_replenishment_suggestions(
        self, 
        tenant_id: UUID, 
        product_ids: List[UUID]
    ) -> List[ReplenishmentSuggestion]:
        """Retorna sugestões de reposição para produtos"""
        raise NotImplementedError
    
    def get_stock_alerts(
        self, 
        tenant_id: UUID,
        risk_level: Optional[str] = None
    ) -> List[StockAlert]:
        """Retorna alertas de risco de ruptura"""
        raise NotImplementedError
    
    def register_sale(
        self,
        tenant_id: UUID,
        sale_data: SaleEvent
    ) -> None:
        """Registra venda para atualizar histórico"""
        raise NotImplementedError
```

### 2. DTOs (Data Transfer Objects)

**Inputs genéricos**:
- Não contêm lógica de negócio do vertical
- Apenas dados estruturados (Pydantic models ou dataclasses)

**Outputs genéricos**:
- Não dependem de entidades do vertical
- Formatos JSON simples e interpretáveis

### 3. Event-Driven Integration

**Eventos enviados pelo Vertical**:
- `pedido_entregue` → Stock Intelligence
- `preco_fornecedor_registrado` → Pricing & Supplier
- `pedido_pronto_entrega` → Delivery & Fulfillment
- `venda_concluida` → Sales Intelligence

**Eventos recebidos do Engines**:
- `alerta_ruptura` ← Stock Intelligence
- `variação_preco` ← Pricing & Supplier
- `entrega_finalizada` ← Delivery & Fulfillment
- `sugestao_produto` ← Sales Intelligence

---

## Estratégia de Implementação (MVP 2)

### Fase 1: Skeleton de Integração

**Objetivo**: Preparar contratos e wiring sem alterar comportamento do MVP 1.

**Tarefas**:
1. Criar camada `app/core_engines/` (ou equivalente)
2. Definir interfaces/ports para cada engine
3. Criar DTOs de input/output (Pydantic)
4. Implementar stubs (lança NotImplementedError ou retorna vazio)
5. Adicionar pontos de chamada nos services existentes
6. **NÃO alterar lógica de negócio do MVP 1**

### Fase 2: Implementação Gradual (MVP 2+)

**Stock Intelligence**:
- Implementar cálculo de sugestões básicas
- Alimentar com histórico de vendas (pedidos entregues)
- Exibir alertas no dashboard

**Pricing & Supplier**:
- Implementar comparação de fornecedores
- Calcular custo base
- Integrar com cadastro de fornecedores

**Delivery & Fulfillment**:
- Implementar planejamento de rotas básico
- Controlar status de entrega
- Registrar prova de entrega

**Sales Intelligence**:
- Implementar sugestões de produtos complementares
- Alimentar com histórico de vendas
- Exibir sugestões durante criação de cotação

---

## Princípios de Evolução

### 1. Backward Compatibility

- Interfaces de engines não mudam de forma breaking
- Novos campos são opcionais
- Versão de API permite evolução

### 2. Isolamento de Engines

- Engines não dependem uns dos outros diretamente
- Comunicação via eventos ou via vertical
- Engines podem evoluir independentemente

### 3. Falha Graceful

- Se engine não disponível, vertical continua funcionando
- Stubs retornam valores vazios ou defaults
- Usuário não vê erro, apenas não vê sugestões

### 4. Configuração Flexível

- Vertical pode habilitar/desabilitar engines
- Configurações por tenant
- Engines podem ser substituídos (plug-and-play)

---

## Observações Importantes

### 1. Engines Não Conhecem o Vertical

- Engines não sabem que é "Materiais de Construção"
- Apenas processam dados genéricos
- Vertical interpreta outputs no contexto do setor

### 2. Vertical Decide Tudo

- Engines apenas sugerem, recomendam, informam
- Vertical decide se segue ou ignora
- Vertical executa ações comerciais

### 3. Preparação para Expansão

- Engines são horizontais e reutilizáveis
- Futuros verticais (alimentação, varejo) podem consumir
- Interfaces genéricas permitem expansão

---

## Próximos Passos

1. ✅ Documentação completa (MVP 2 - Parte A)
2. ⏭️ Implementar skeleton de integração (MVP 2 - Parte B)
3. ⏭️ Implementar engines gradualmente (MVP 2+)
4. ⏭️ Integrar engines com vertical (MVP 2+)
5. ⏭️ Validar integração com testes (MVP 2+)

---

**Última atualização**: Janeiro 2026  
**Versão**: 2.0 (MVP 2 - Documentação)  
**Status**: ✅ Documentação Completa

