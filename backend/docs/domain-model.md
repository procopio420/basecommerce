# Modelo de Domínio - Vertical Materiais de Construção

## Visão Geral

Este documento descreve o modelo de domínio implementado para o vertical de materiais de construção, conforme definido na documentação (`docs/01-domain-model.md`).

## Entidades do Domínio

### 1. Tenant (Loja)

**Responsabilidade**: Representa uma loja física que usa o sistema (multi-tenant).

**Atributos**:
- `id`: UUID (chave primária)
- `nome`: Nome da loja
- `cnpj`: CNPJ da loja
- `endereco`: Endereço completo
- `contato`: Telefone, email
- `status`: Ativo/Inativo
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Tem múltiplos usuários (funcionários)
- Tem múltiplos clientes
- Tem múltiplos produtos (catálogo)
- Gera múltiplas cotações e pedidos

**Observações**:
- Isolamento total: Cada loja só vê seus próprios dados
- Núcleo do sistema multi-tenant

**Localização**: `app/models/tenant.py`

---

### 2. Cliente

**Responsabilidade**: Representa quem compra na loja (PF ou PJ).

**Tipos**:
- **Pessoa Física (PF)**: Consumidor final, compra no balcão
- **Pessoa Jurídica (PJ)**: Obra, construtora, empreiteiro

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `tipo`: String ('PF' ou 'PJ')
- `nome`: Nome/Razão Social
- `documento`: CPF/CNPJ (único por loja)
- `email`: Email de contato
- `telefone`: Telefone de contato
- `endereco`, `cidade`, `estado`, `cep`: Endereço completo
- `observacoes`: Texto livre
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a uma loja (tenant)
- Pode ter múltiplas obras (se PJ)
- Recebe múltiplas cotações
- Tem múltiplos pedidos

**Observações**:
- Núcleo do sistema
- Documento (CPF/CNPJ) é único por loja
- Endereço importante para entrega

**Localização**: `app/models/cliente.py`

---

### 3. Obra

**Responsabilidade**: Representa um local de construção/obra vinculado a um cliente PJ.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `cliente_id`: UUID (FK para Cliente - obrigatório)
- `nome`: Nome da obra
- `endereco`, `cidade`, `estado`: Endereço completo
- `observacoes`: Texto livre
- `ativa`: Boolean (status)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a um cliente (obrigatório)
- Pertence a uma loja (tenant)
- Pode ter cotações específicas
- Pode ter pedidos específicos

**Observações**:
- Opcional: Cliente pode não ter obra (compra geral)
- Permite diferenciar preços e entregas por obra
- Núcleo do sistema (opcional mas comum)

**Localização**: `app/models/obra.py`

---

### 4. Produto

**Responsabilidade**: Representa um item vendido pela loja.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `codigo`: Código interno (opcional, único por loja)
- `nome`: Nome do produto
- `descricao`: Descrição do produto
- `unidade`: Unidade de medida ('UN', 'KG', 'M', 'M²', 'M³')
- `preco_base`: Preço base
- `ativo`: Boolean (status)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a uma loja (tenant)
- Aparece em múltiplas cotações
- Aparece em múltiplos pedidos
- Tem histórico de preços

**Observações**:
- Núcleo do sistema
- Preço base pode ser alterado ao longo do tempo (histórico)
- Unidade importante para cálculos

**Localização**: `app/models/produto.py`

---

### 5. Cotação

**Responsabilidade**: Representa uma proposta de venda enviada a um cliente.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `cliente_id`: UUID (FK para Cliente - obrigatório)
- `obra_id`: UUID (FK para Obra - opcional)
- `numero`: String (número único, formato COT-001)
- `status`: String ('rascunho', 'enviada', 'aprovada', 'convertida', 'cancelada')
- `desconto_percentual`: Decimal (desconto geral)
- `observacoes`: Texto livre
- `validade_dias`: Integer (validade em dias)
- `usuario_id`: UUID (FK para User - vendedor responsável)
- `enviada_em`: DateTime (quando foi enviada)
- `aprovada_em`: DateTime (quando foi aprovada)
- `convertida_em`: DateTime (quando foi convertida em pedido)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a uma loja (tenant)
- É para um cliente específico
- Pode estar vinculada a uma obra
- Tem múltiplos itens (CotacaoItem)
- Pode gerar um pedido (quando convertida)
- Criada por um usuário (vendedor)

**Observações**:
- Núcleo do sistema (MVP 1)
- Versão rascunho permite edição
- Quando convertida, não pode mais ser editada
- Histórico preservado mesmo após conversão

**Localização**: `app/models/cotacao.py`

**Regras de Domínio** (ver `app/domain/cotacao/`):
- Apenas cotações em rascunho podem ser editadas
- Apenas cotações em rascunho podem ser enviadas
- Apenas cotações enviadas podem ser aprovadas
- Apenas cotações aprovadas podem ser convertidas em pedido
- Cotação deve ter pelo menos 1 item para ser enviada

---

### 6. CotacaoItem

**Responsabilidade**: Representa um produto na cotação com quantidade e preço.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `cotacao_id`: UUID (FK para Cotacao - obrigatório)
- `produto_id`: UUID (FK para Produto - obrigatório)
- `quantidade`: Decimal (quantidade)
- `preco_unitario`: Decimal (preço unitário "congelado")
- `desconto_percentual`: Decimal (desconto do item)
- `valor_total`: Decimal (valor total calculado)
- `observacoes`: Texto livre
- `ordem`: Integer (ordem de exibição)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a uma cotação
- Referencia um produto
- Pertence a uma loja (tenant)

**Observações**:
- Núcleo do sistema (MVP 1)
- Preço unitário é "congelado" no momento da cotação
- Valor total = (quantidade × preco_unitario) × (1 - desconto/100)

**Localização**: `app/models/cotacao.py`

---

### 7. Pedido

**Responsabilidade**: Representa uma venda confirmada que será entregue.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `cotacao_id`: UUID (FK para Cotacao - opcional, se veio de cotação)
- `cliente_id`: UUID (FK para Cliente - obrigatório)
- `obra_id`: UUID (FK para Obra - opcional)
- `numero`: String (número único, formato PED-001)
- `status`: String ('pendente', 'em_preparacao', 'saiu_entrega', 'entregue', 'cancelado')
- `desconto_percentual`: Decimal (desconto geral)
- `observacoes`: Texto livre
- `usuario_id`: UUID (FK para User - vendedor responsável)
- `entregue_em`: DateTime (quando foi entregue)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a uma loja (tenant)
- É para um cliente específico
- Pode estar vinculado a uma obra
- Pode ter vindo de uma cotação
- Tem múltiplos itens (PedidoItem)
- Criado por um usuário

**Observações**:
- Núcleo do sistema (MVP 1)
- Pode ser criado direto ou convertido de cotação
- Status permite rastreamento da entrega
- Imutável após criação (apenas status muda)

**Localização**: `app/models/pedido.py`

**Regras de Domínio** (ver `app/domain/pedido/`):
- Pedido não pode ser editado após criação (apenas status)
- Pedido entregue não pode ser cancelado
- Conversão de cotação: apenas cotações aprovadas podem ser convertidas
- Conversão de cotação: cotação não pode ter sido convertida antes
- Conversão de cotação: cotação deve ter pelo menos 1 item

---

### 8. PedidoItem

**Responsabilidade**: Representa um produto no pedido com quantidade e preço.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `pedido_id`: UUID (FK para Pedido - obrigatório)
- `produto_id`: UUID (FK para Produto - obrigatório)
- `quantidade`: Decimal (quantidade)
- `preco_unitario`: Decimal (preço unitário "congelado")
- `desconto_percentual`: Decimal (desconto do item)
- `valor_total`: Decimal (valor total calculado)
- `observacoes`: Texto livre
- `ordem`: Integer (ordem de exibição)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a um pedido
- Referencia um produto
- Pertence a uma loja (tenant)

**Observações**:
- Núcleo do sistema (MVP 1)
- Copiado da cotação quando pedido é convertido
- Pode ser diferente da cotação se pedido foi criado direto
- Preço é "congelado" no momento da criação do pedido

**Localização**: `app/models/pedido.py`

---

### 9. Histórico de Preços

**Responsabilidade**: Registra mudanças de preço de produtos ao longo do tempo.

**Atributos**:
- `id`: UUID (chave primária)
- `tenant_id`: UUID (FK para Tenant)
- `produto_id`: UUID (FK para Produto - obrigatório)
- `preco`: Decimal (preço)
- `data_alteracao`: DateTime (data da alteração)
- `usuario_id`: UUID (FK para User - opcional, quem alterou)
- `created_at`, `updated_at`: Timestamps

**Relações**:
- Pertence a um produto
- Pertence a uma loja (tenant)

**Observações**:
- Núcleo do sistema (suporte a análise futura)
- Permite análise de variação de preços
- Importante para entender margem histórica
- TODO: No futuro, Pricing & Supplier Intelligence Engine pode usar este histórico

**Localização**: `app/models/historico_preco.py`

---

## Entidades Futuras (Não Implementadas no MVP 1)

### Estoque (MVP 2)

**Observação**: Estoque será implementado no MVP 2.

**TODO**: 
- Consumirá Stock Intelligence Engine para obter alertas e sugestões
- Não armazenará estoque mínimo/máximo (vem do engine)
- Ver `docs/core-stock-intelligence.md`

---

### Entrega (MVP 3)

**Observação**: Entrega será implementada no MVP 3.

**TODO**:
- Consumirá Delivery & Fulfillment Engine para planejar rotas
- Ver `docs/core-delivery-fulfillment.md`

---

## Princípios de Design

### 1. Multi-tenant com Isolamento Total

Cada loja (tenant) tem isolamento completo de dados. Nenhuma loja vê dados de outra.

**Implementação**: Todos os models têm `tenant_id` e queries filtram por tenant.

---

### 2. Versionamento e Histórico

- Preços têm histórico (`HistoricoPreco`)
- Cotações preservam estado mesmo após conversão
- Pedidos não mudam após criação (imutabilidade)

**Implementação**: 
- Histórico de preços registrado automaticamente (TODO: implementar trigger/hook)
- Status de cotação preservado após conversão
- Pedido imutável após criação

---

### 3. Imutabilidade de Dados Críticos

- Pedido não pode ser editado após criação (apenas status)
- Cotação convertida não pode ser editada
- Preço em itens é "congelado" no momento da cotação/pedido

**Implementação**: 
- Regras de domínio em `app/domain/pedido/exceptions.py`
- Regras de domínio em `app/domain/cotacao/exceptions.py`
- Preços copiados (não referenciados) na conversão

---

### 4. Opcionalidade Intencional

- Obra é opcional (cliente pode não ter obra)
- Pedido pode ser criado direto sem cotação
- Desconto pode ser zero

**Implementação**: Campos `obra_id` e `cotacao_id` são opcionais nos models.

---

### 5. Simplicidade sobre Completude

- Não tenta modelar tudo
- Foca no que resolve o problema real (MVP 1)
- Expansível quando necessário

**Implementação**: Apenas entidades do núcleo (MVP 1) foram implementadas.

---

## Integração com Engines (Futuro)

### Stock Intelligence Engine (MVP 2)

**Quando**: MVP 2

**Onde**:
- Módulo de Estoque consultará engine para sugestões de reposição
- Pedido entregue atualizará dados enviados ao engine

**TODO**: 
```python
# app/application/services/pedido_service.py
# TODO: No futuro, Stock Intelligence Engine será atualizado aqui
# Exemplo: stock_engine.update_stock_after_delivery(pedido)
```

---

### Pricing & Supplier Intelligence Engine (MVP 2+)

**Quando**: MVP 2+

**Onde**:
- Histórico de preços será usado para comparar fornecedores
- Sugestões de fornecedor mais vantajoso

**TODO**:
```python
# app/models/historico_preco.py
# TODO: Pricing & Supplier Intelligence Engine pode usar este histórico
```

---

### Delivery & Fulfillment Engine (MVP 3)

**Quando**: MVP 3

**Onde**:
- Planejamento de entregas
- Roteirização

**TODO**:
```python
# app/application/services/pedido_service.py
# TODO: No futuro, Delivery & Fulfillment Engine será usado aqui
# Exemplo: delivery_engine.plan_routes(pedidos_prontos_entrega)
```

---

### Sales Intelligence Engine (MVP 1+)

**Quando**: MVP 1+ (pode ser usado nas cotações)

**Onde**:
- Sugestões de produtos complementares durante criação de cotação

**TODO**:
```python
# app/application/services/cotacao_service.py
# TODO: No futuro, Sales Intelligence Engine será consultado aqui
# Exemplo: sales_engine.suggest_complementary_products(produtos_no_carrinho)
```

---

## Estrutura de Arquivos

```
app/
├── models/              # Models SQLAlchemy (infraestrutura)
│   ├── tenant.py
│   ├── cliente.py
│   ├── obra.py
│   ├── produto.py
│   ├── cotacao.py       # Cotacao + CotacaoItem
│   ├── pedido.py        # Pedido + PedidoItem
│   └── historico_preco.py
│
├── domain/              # Regras de domínio (puro)
│   ├── cotacao/
│   │   ├── exceptions.py
│   │   └── validators.py
│   └── pedido/
│       ├── exceptions.py
│       └── validators.py
│
└── application/         # Serviços de aplicação (casos de uso)
    └── services/
        ├── cotacao_service.py
        └── pedido_service.py
```

---

**Última atualização**: Janeiro 2026
**Versão**: 1.0

