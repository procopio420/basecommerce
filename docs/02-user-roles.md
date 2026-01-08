# Papéis de Usuário e Permissões

## Visão Geral

O sistema suporta diferentes papéis de usuário, cada um com responsabilidades e permissões específicas. Cada usuário pertence a uma loja (tenant) e só pode ver/dados da sua loja.

---

## Papéis Principais

### 1. Dono da Loja (Admin)

**Responsabilidade**: Gerencia a loja e tem visibilidade completa.

**O Que Faz**:
- ✅ Visualiza todas as cotações e pedidos
- ✅ Acessa dashboard com métricas gerais
- ✅ Cria e edita produtos (catálogo)
- ✅ Cria e edita clientes
- ✅ Define regras de preço (tabela base, descontos)
- ✅ Converte cotação em pedido
- ✅ Atualiza status de pedidos
- ✅ Acessa relatórios e análises
- ✅ Gerencia usuários (cria, edita, desativa)
- ✅ Configurações da loja

**O Que NÃO Pode Fazer**:
- ❌ Não deleta dados históricos (auditoria)
- ❌ Não vê dados de outras lojas
- ❌ Não altera pedido após criação (apenas status)

**Fluxos que Participa**:
- Todos os fluxos (criação, edição, aprovação, entrega)
- Configuração inicial da loja
- Análise de desempenho

**Observações**:
- Papel mais poderoso
- Geralmente 1-2 usuários por loja
- Deve ter acesso a tudo para resolver problemas

---

### 2. Vendedor de Balcão (Vendedor)

**Responsabilidade**: Atende clientes no balcão e cria cotações rapidamente.

**O Que Faz**:
- ✅ Cria cotações (rascunho e envia)
- ✅ Edita cotações em rascunho
- ✅ Busca clientes e produtos
- ✅ Cria novos clientes (se não existir)
- ✅ Converte cotação aprovada em pedido
- ✅ Visualiza cotações e pedidos que criou
- ✅ Visualiza status de pedidos

**O Que NÃO Pode Fazer**:
- ❌ Não aprova cotações (apenas envia)
- ❌ Não altera preços de produtos
- ❌ Não deleta cotações ou pedidos
- ❌ Não vê cotações/pedidos de outros vendedores (futuro: pode ser configurável)
- ❌ Não altera status de pedido para "entregue"
- ❌ Não configura nada

**Fluxos que Participa**:
- Fluxo de cotação (criação, edição, envio)
- Fluxo de conversão cotação → pedido
- Busca de clientes e produtos

**Observações**:
- Papel mais comum na loja (3-10 usuários)
- Interface deve ser rápida e simples
- Foco em produtividade, não em controle

---

### 3. Financeiro

**Responsabilidade**: Acompanha receitas, pendências e financeiro da loja.

**O Que Faz**:
- ✅ Visualiza todas as cotações e pedidos
- ✅ Acessa dashboard com receitas
- ✅ Marca cotações como aprovadas (após pagamento ou compromisso)
- ✅ Acompanha status de pedidos
- ✅ Visualiza relatórios financeiros (futuro)
- ✅ Exporta dados para planilhas (futuro)

**O Que NÃO Pode Fazer**:
- ❌ Não cria cotações ou pedidos
- ❌ Não altera preços de produtos
- ❌ Não altera clientes ou obras
- ❌ Não altera status de pedido para "entregue"
- ❌ Não configura nada

**Fluxos que Participa**:
- Fluxo de cotação (aprovação após compromisso/pagamento)
- Acompanhamento de pedidos entregues

**Observações**:
- Papel geralmente 1 usuário por loja
- Foco em visibilidade, não em operação
- Futuro: pode ter acesso a módulo financeiro completo

---

### 4. Estoquista

**Responsabilidade**: Gerencia estoque físico e consome alertas/sugestões do Stock Intelligence Engine (MVP 2+).

**O Que Faz**:
- ✅ Visualiza estoque atual (físico)
- ✅ Recebe alertas de risco de ruptura (do Stock Intelligence Engine)
- ✅ Visualiza sugestões de reposição (do Stock Intelligence Engine)
- ✅ Visualiza análise ABC (do Stock Intelligence Engine)
- ✅ Atualiza quantidade de estoque físico (entradas/saídas)
- ✅ Visualiza histórico de movimentação (futuro)
- ✅ Configura parâmetros de reposição para o engine (lead time, estoque de segurança)

**O Que NÃO Pode Fazer**:
- ❌ Não cria cotações ou pedidos
- ❌ Não altera preços
- ❌ Não altera clientes
- ❌ Não modifica o Stock Intelligence Engine (engine é core, não é responsabilidade do vertical)
- ❌ Não configura algoritmos do engine (apenas parâmetros de reposição)

**Fluxos que Participa**:
- Fluxo de reposição de estoque (MVP 2) - consome sugestões do Stock Intelligence Engine
- Gestão de estoque físico (atualização de quantidade)
- Visualização de pedidos para planejamento (futuro)

**Observações**:
- Papel geralmente 1 usuário por loja
- No MVP 1, pode não existir (dono faz)
- Será importante no MVP 2 (Gestão de Estoque + Stock Intelligence Engine)
- **Interage com**: Stock Intelligence Engine (core) via módulo de Gestão de Estoque (vertical)

---

### 5. Motorista

**Responsabilidade**: Entrega pedidos e registra prova de entrega (MVP 3+).

**O Que Faz**:
- ✅ Visualiza pedidos atribuídos para entrega
- ✅ Atualiza status de pedido (saiu, chegou)
- ✅ Registra prova de entrega (foto, assinatura) (futuro)
- ✅ Visualiza rota de entrega (futuro)

**O Que NÃO Pode Fazer**:
- ❌ Não cria ou edita pedidos
- ❌ Não altera quantidades ou produtos
- ❌ Não vê cotações
- ❌ Não configura nada

**Fluxos que Participa**:
- Fluxo de entrega (MVP 3)
- Registro de prova de entrega

**Observações**:
- Papel geralmente 2-5 usuários por loja
- No MVP 1-2, pode não existir (funcionalidade manual)
- Será importante no MVP 3 (Logística)
- Interface será mobile-first (futuro: app)

---

### 6. Cliente B2B (Externo - Futuro)

**Responsabilidade**: Visualiza cotações e aprova compras (MVP 4+).

**O Que Faz**:
- ✅ Recebe cotações por email/link
- ✅ Visualiza cotações enviadas
- ✅ Aprova ou rejeita cotações
- ✅ Visualiza catálogo personalizado (futuro)
- ✅ Faz pedidos direto (futuro: e-commerce B2B)
- ✅ Visualiza histórico de pedidos (futuro)

**O Que NÃO Pode Fazer**:
- ❌ Não cria produtos
- ❌ Não altera preços
- ❌ Não vê dados de outros clientes
- ❌ Não acessa sistema interno da loja

**Fluxos que Participa**:
- Fluxo de cotação (visualização e aprovação)
- Fluxo de recompra (futuro: e-commerce B2B)

**Observações**:
- Papel externo (não é funcionário)
- No MVP 1-3, aprovação é manual (vendedor marca como aprovada)
- Será importante no MVP 4 (E-commerce B2B)
- Interface será mobile-friendly

---

### 7. Cliente B2C (Consumidor Final)

**Responsabilidade**: Compra no balcão, não acessa sistema (atualmente).

**O Que Faz**:
- ✅ Recebe cotação/pedido via WhatsApp ou impresso (vendedor cria)
- ✅ Não acessa sistema (no MVP 1-3)
- ✅ Futuro: pode ter acesso básico para ver status de pedido

**O Que NÃO Pode Fazer**:
- ❌ Não acessa sistema (no MVP 1-3)
- ❌ Não cria cotações
- ❌ Não aprova online

**Fluxos que Participa**:
- Fluxo de cotação (via vendedor)
- Fluxo de pedido (via vendedor)

**Observações**:
- Não é usuário do sistema no MVP 1-3
- Interação é via vendedor no balcão
- Futuro: pode ter portal básico

---

## Matriz de Permissões

| Funcionalidade | Admin | Vendedor | Financeiro | Estoquista | Motorista |
|----------------|-------|----------|------------|------------|-----------|
| **Cotações** |
| Criar cotação | ✅ | ✅ | ❌ | ❌ | ❌ |
| Editar cotação (rascunho) | ✅ | ✅ | ❌ | ❌ | ❌ |
| Enviar cotação | ✅ | ✅ | ❌ | ❌ | ❌ |
| Aprovar cotação | ✅ | ❌ | ✅ | ❌ | ❌ |
| Ver todas cotações | ✅ | ❌ | ✅ | ❌ | ❌ |
| Ver próprias cotações | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Pedidos** |
| Criar pedido | ✅ | ✅ | ❌ | ❌ | ❌ |
| Converter cotação → pedido | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver todos pedidos | ✅ | ❌ | ✅ | ❌ | ❌ |
| Ver próprios pedidos | ✅ | ✅ | ✅ | ❌ | ❌ |
| Atualizar status pedido | ✅ | ⚠️ | ❌ | ❌ | ✅ |
| Marcar como entregue | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Clientes** |
| Criar cliente | ✅ | ✅ | ❌ | ❌ | ❌ |
| Editar cliente | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Ver todos clientes | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Produtos** |
| Criar produto | ✅ | ❌ | ❌ | ❌ | ❌ |
| Editar produto | ✅ | ❌ | ❌ | ❌ | ❌ |
| Alterar preço | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver produtos | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Estoque (MVP 2+)** |
| Ver estoque | ✅ | ❌ | ❌ | ✅ | ❌ |
| Atualizar estoque | ✅ | ❌ | ❌ | ✅ | ❌ |
| Ver alertas | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Configurações** |
| Configurar loja | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gerenciar usuários | ✅ | ❌ | ❌ | ❌ | ❌ |
| Acessar relatórios | ✅ | ❌ | ✅ | ❌ | ❌ |

**Legenda**:
- ✅ = Permissão total
- ⚠️ = Permissão limitada (ex: vendedor pode editar cliente que criou)
- ❌ = Sem permissão

---

## Hierarquia de Papéis

```
Admin (Dono)
  ├── Pode fazer tudo
  ├── Gerencia vendedores
  └── Tem acesso a relatórios

Vendedor
  ├── Foco em criação de cotações
  ├── Pode converter em pedidos
  └── Visualiza apenas o que criou

Financeiro
  ├── Aprova cotações
  ├── Visualiza tudo
  └── Foco em acompanhamento

Estoquista (MVP 2+)
  ├── Gerencia estoque
  └── Visualiza produtos e alertas

Motorista (MVP 3+)
  ├── Entrega pedidos
  └── Registra prova de entrega
```

---

## Observações Importantes

### 1. Isolamento por Loja

Todos os papéis só veem dados da sua loja. Não há vazamento de dados entre lojas.

### 2. Evolução dos Papéis

- **MVP 1**: Admin e Vendedor são suficientes
- **MVP 2**: Adicionar Estoquista
- **MVP 3**: Adicionar Motorista
- **MVP 4**: Adicionar Cliente B2B (externo)

### 3. Permissões Configuráveis (Futuro)

No futuro, permissões podem ser configuráveis por loja (ex: vendedor pode ver todas as cotações, não apenas as próprias).

### 4. Auditoria

Todas as ações são registradas com usuário que executou, independente do papel.

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

