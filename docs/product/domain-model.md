# Modelo de Domínio

## Visão Geral

O domínio do negócio é focado em **lojas de materiais de construção** que vendem para **obras** e **consumidores finais**, operando através de **cotações** que se tornam **pedidos** e são **entregues** por **motoristas**.

## Entidades Principais

### Tenant (Loja)

**Responsabilidade**: Representa uma loja física que usa o sistema.

**Atributos**:
- Nome da loja
- CNPJ
- Endereço completo
- Contato (telefone, email)
- Status (ativo/inativo)

**Relações**:
- Tem múltiplos usuários (funcionários)
- Tem múltiplos clientes
- Tem múltiplos produtos (catálogo)
- Gera múltiplas cotações e pedidos

**Observações**:
- Isolamento total: Cada loja só vê seus próprios dados
- Núcleo do sistema multi-tenant

---

### Cliente

**Responsabilidade**: Representa quem compra na loja (PF ou PJ).

**Tipos**:
- **Pessoa Física (PF)**: Consumidor final, compra no balcão
- **Pessoa Jurídica (PJ)**: Obra, construtora, empreiteiro

**Atributos**:
- Tipo (PF/PJ)
- Nome/Razão Social
- CPF/CNPJ (documento único por loja)
- Contato (telefone, email)
- Endereço completo

**Relações**:
- Pertence a uma loja (tenant)
- Pode ter múltiplas obras (se PJ)
- Recebe múltiplas cotações
- Tem múltiplos pedidos
- Pode ter regras de preço específicas (futuro)

**Observações**:
- Núcleo do sistema
- Documento (CPF/CNPJ) é único por loja
- Endereço importante para entrega

---

### Obra

**Responsabilidade**: Representa um local de construção/obra vinculado a um cliente PJ.

**Atributos**:
- Nome da obra
- Endereço completo
- Cliente proprietário
- Status (ativa/inativa)
- Observações

**Relações**:
- Pertence a um cliente (obrigatório)
- Pertence a uma loja (tenant)
- Pode ter cotações específicas
- Pode ter pedidos específicos
- Pode ter preços diferenciados (futuro)

**Observações**:
- Opcional: Cliente pode não ter obra (compra geral)
- Permite diferenciar preços e entregas por obra
- Núcleo do sistema (opcional mas comum)

---

### Produto

**Responsabilidade**: Representa um item vendido pela loja.

**Atributos**:
- Código interno (opcional, único por loja)
- Nome
- Descrição
- Unidade de medida (UN, KG, M, M², M³)
- Preço base
- Status (ativo/inativo)

**Relações**:
- Pertence a uma loja (tenant)
- Aparece em múltiplas cotações
- Aparece em múltiplos pedidos
- Tem histórico de preços
- Pode ter estoque (futuro)

**Observações**:
- Núcleo do sistema
- Preço base pode ser alterado ao longo do tempo (histórico)
- Unidade importante para cálculos

---

### Cotação

**Responsabilidade**: Representa uma proposta de venda enviada a um cliente.

**Atributos**:
- Número único (gerado automaticamente)
- Cliente destinatário
- Obra (opcional)
- Status (rascunho, enviada, aprovada, convertida, cancelada)
- Desconto percentual geral
- Validade (dias)
- Data de criação, envio, aprovação, conversão
- Vendedor responsável
- Observações

**Relações**:
- Pertence a uma loja (tenant)
- É para um cliente específico
- Pode estar vinculada a uma obra
- Tem múltiplos itens (produtos com quantidades)
- Pode gerar um pedido (quando convertida)
- Criada por um usuário (vendedor)

**Observações**:
- Núcleo do sistema (MVP 1)
- Versão rascunho permite edição
- Quando convertida, não pode mais ser editada
- Histórico preservado mesmo após conversão

---

### Cotação Item

**Responsabilidade**: Representa um produto na cotação com quantidade e preço.

**Atributos**:
- Produto
- Quantidade
- Preço unitário (na hora da cotação)
- Desconto percentual do item
- Valor total calculado
- Ordem de exibição
- Observações

**Relações**:
- Pertence a uma cotação
- Referencia um produto
- Pertence a uma loja (tenant)

**Observações**:
- Núcleo do sistema (MVP 1)
- Preço unitário é "congelado" no momento da cotação
- Valor total = (quantidade × preço_unitário) × (1 - desconto/100)

---

### Pedido

**Responsabilidade**: Representa uma venda confirmada que será entregue.

**Atributos**:
- Número único (gerado automaticamente)
- Cliente
- Obra (opcional)
- Cotação origem (opcional, se foi convertida de cotação)
- Status (pendente, em_preparacao, saiu_entrega, entregue, cancelado)
- Desconto percentual geral
- Data de criação, entrega
- Motorista responsável (futuro)
- Prova de entrega (futuro: foto, assinatura)
- Vendedor responsável
- Observações

**Relações**:
- Pertence a uma loja (tenant)
- É para um cliente específico
- Pode estar vinculado a uma obra
- Pode ter vindo de uma cotação
- Tem múltiplos itens (produtos com quantidades)
- Criado por um usuário

**Observações**:
- Núcleo do sistema (MVP 1)
- Pode ser criado direto ou convertido de cotação
- Status permite rastreamento da entrega

---

### Pedido Item

**Responsabilidade**: Representa um produto no pedido com quantidade e preço.

**Atributos**:
- Produto
- Quantidade
- Preço unitário
- Desconto percentual do item
- Valor total calculado
- Ordem de exibição
- Observações

**Relações**:
- Pertence a um pedido
- Referencia um produto
- Pertence a uma loja (tenant)

**Observações**:
- Núcleo do sistema (MVP 1)
- Copiado da cotação quando pedido é convertido
- Pode ser diferente da cotação se pedido foi criado direto

---

### Histórico de Preços

**Responsabilidade**: Registra mudanças de preço de produtos ao longo do tempo.

**Atributos**:
- Produto
- Preço
- Data da alteração
- Usuário que alterou (opcional)

**Relações**:
- Pertence a um produto
- Pertence a uma loja (tenant)

**Observações**:
- Núcleo do sistema (suporte a análise futura)
- Permite análise de variação de preços
- Importante para entender margem histórica

---

### Estoque (Vertical - MVP 2)

**Responsabilidade**: Representa quantidade disponível de produtos no contexto do vertical de materiais de construção.

**Atributos**:
- Produto
- Quantidade atual
- Última atualização
- Entradas/saídas (movimentação física)

**Relações**:
- Pertence a um produto
- Pertence a uma loja (tenant)
- Vinculado a pedidos entregues (atualiza estoque)

**Observações**:
- Módulo vertical (MVP 2)
- Gerencia estoque físico (entradas/saídas)
- Consome **Stock Intelligence Engine** para obter alertas e sugestões
- Estoque mínimo/máximo e análise ABC são fornecidos pelo engine, não armazenados aqui
- **Documentação do Engine**: [core-stock-intelligence.md](./core-stock-intelligence.md)

---

### Entrega (Módulo Futuro)

**Responsabilidade**: Representa uma entrega de pedido em uma obra.

**Atributos**:
- Pedido
- Motorista
- Veículo
- Data/hora saída
- Data/hora chegada
- Prova de entrega (foto, assinatura)
- Observações

**Relações**:
- Pertence a um pedido
- Realizada por um motorista (futuro)
- Usa um veículo (futuro)

**Observações**:
- Módulo futuro (MVP 3)
- Núcleo será criado quando módulo for implementado

---

## Relacionamentos Principais (Tabelas)

### Hierarquia de Dados

```
Tenant (Loja)
  ├── Users (Funcionários)
  ├── Clientes
  │     └── Obras (opcional)
  ├── Produtos
  │     └── Histórico de Preços
  ├── Cotações
  │     └── Cotação Itens
  │           └── Produto
  └── Pedidos
        └── Pedido Itens
              └── Produto
```

### Fluxo de Dados

| Origem | Destino | Relação | Obrigatória |
|--------|---------|---------|-------------|
| Cotação | Pedido | 1 para 0..1 | Não (pedido pode ser criado direto) |
| Cotação | Cliente | N para 1 | Sim |
| Cotação | Obra | N para 0..1 | Não |
| Cotação | Cotação Item | 1 para N | Sim (mínimo 1 item) |
| Cotação Item | Produto | N para 1 | Sim |
| Pedido | Cliente | N para 1 | Sim |
| Pedido | Obra | N para 0..1 | Não |
| Pedido | Pedido Item | 1 para N | Sim (mínimo 1 item) |
| Pedido Item | Produto | N para 1 | Sim |
| Cliente | Obra | 1 para N | Não |
| Produto | Histórico Preço | 1 para N | Não (mas comum) |

---

## Núcleo vs Módulo Futuro

### Núcleo (MVP 1)

Estas entidades são essenciais e devem funcionar desde o início:

- ✅ Tenant
- ✅ Cliente
- ✅ Obra (opcional mas importante)
- ✅ Produto
- ✅ Cotação
- ✅ Cotação Item
- ✅ Pedido
- ✅ Pedido Item
- ✅ Histórico de Preços (base para futuras análises)

### Módulos Futuros

Estas entidades serão adicionadas conforme os módulos são implementados:

- 📦 Estoque (Vertical - MVP 2) - Consome Stock Intelligence Engine
- 🚚 Entrega, Motorista, Veículo (Vertical - MVP 3)
- 🛒 Catálogo Personalizado por Cliente (Vertical - MVP 4)
- 📊 Relatórios Avançados (MVP 5+)
- 💰 Financeiro (MVP 5+)

### Core Modules (Horizontais)

**Stock Intelligence Engine (MVP 2)**:
- ✅ Análise de histórico de vendas (genérico)
- ✅ Cálculo de estoque mínimo/máximo (genérico)
- ✅ Detecção de risco de ruptura (genérico)
- ✅ Sugestão de reposição (genérico)
- ✅ Análise ABC (genérico)

**Observações**:
- Engine não tem entidades próprias no domínio do vertical
- Engine consome dados do vertical (vendas, estoque) e retorna inteligência
- Engine é reutilizável por outros verticais no futuro
- **Documentação completa**: [core-stock-intelligence.md](./core-stock-intelligence.md)

---

## Princípios de Design

### 1. Multi-tenant com Isolamento Total

Cada loja (tenant) tem isolamento completo de dados. Nenhuma loja vê dados de outra.

### 2. Versionamento e Histórico

- Preços têm histórico
- Cotações preservam estado mesmo após conversão
- Pedidos não mudam após criação (imutabilidade)

### 3. Imutabilidade de Dados Críticos

- Pedido não pode ser editado após criação (apenas status)
- Cotação convertida não pode ser editada
- Preço em itens é "congelado" no momento da cotação/pedido

### 4. Opcionalidade Intencional

- Obra é opcional (cliente pode não ter obra)
- Pedido pode ser criado direto sem cotação
- Desconto pode ser zero

### 5. Simplicidade sobre Completude

- Não tenta modelar tudo
- Foca no que resolve o problema real
- Expansível quando necessário

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

