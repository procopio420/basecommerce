# Não-Objetivos do Sistema

## Visão Geral

Este documento lista explicitamente o que **NÃO será feito** no produto, o que **não é prioridade**, o que **só entra após validação**, e o que **nunca será objetivo** do sistema.

---

## O Que NÃO Será Feito

### 1. Sistema Fiscal Completo

**Não fazemos**:
- ❌ Emissão de notas fiscais
- ❌ Cálculo de impostos
- ❌ Integração com SEFAZ
- ❌ Sped fiscal
- ❌ Contabilidade completa

**Por quê**: É complexo, regulatório e há sistemas especializados (TOTVS, Senior, etc.).

**O que fazemos**:
- ✅ Integração com sistemas fiscais existentes (futuro: MVP 5+)
- ✅ Exportação de dados para sistemas fiscais (futuro)

---

### 2. Gestão Financeira Completa

**Não fazemos**:
- ❌ Contas a pagar
- ❌ Contas a receber
- ❌ Fluxo de caixa completo
- ❌ Conciliação bancária
- ❌ Folha de pagamento

**Por quê**: É complexo e há sistemas especializados.

**O que fazemos**:
- ✅ Dashboard com receitas (métricas básicas)
- ✅ Acompanhamento de pedidos pendentes
- ✅ Exportação de dados para sistemas financeiros (futuro)

---

### 3. Gestão de Obras

**Não fazemos**:
- ❌ Cronograma de obras
- ❌ Gestão de equipe
- ❌ Avanço físico
- ❌ Orçamento de obra
- ❌ Controle de custos de obra

**Por quê**: É outro domínio de negócio. Obras são clientes, não é nosso core.

**O que fazemos**:
- ✅ Vinculamos obras aos clientes
- ✅ Permitimos preços diferenciados por obra (futuro)
- ✅ Rastreamos entregas por obra

---

### 4. Marketplace ou Conecta Lojas

**Não fazemos**:
- ❌ Conectar múltiplas lojas
- ❌ Marketplace para comparar preços
- ❌ Integração entre lojas
- ❌ Compartilhamento de estoque entre lojas

**Por quê**: Cada loja é independente. Não queremos competir com marketplaces.

**O que fazemos**:
- ✅ Cada loja tem isolamento total de dados
- ✅ Cada loja gerencia seu próprio catálogo

---

### 5. E-commerce B2C (Consumidor Final)

**Não fazemos**:
- ❌ Site de vendas para consumidor final
- ❌ Catálogo público
- ❌ Checkout público
- ❌ Pagamento online para B2C

**Por quê**: Foco é B2B (obras) e balcão. B2C é outro mercado.

**O que fazemos**:
- ✅ Atendimento no balcão (B2C via vendedor)
- ✅ Portal B2B para obras (MVP 4)

---

### 6. Gestão de Fornecedores

**Não fazemos**:
- ❌ Cadastro de fornecedores
- ❌ Ordem de compra para fornecedores
- ❌ Integração com fornecedores
- ❌ Gestão de compras

**Por quê**: Foco é venda (downstream), não compra (upstream).

**O que fazemos**:
- ✅ Sugestão de reposição (MVP 2)
- ✅ Exportação de lista de compras (futuro)

---

### 7. App Mobile Nativo

**Não fazemos** (no MVP 1-4):
- ❌ App iOS nativo
- ❌ App Android nativo
- ❌ Desenvolvimento mobile nativo

**Por quê**: Custo e complexidade. Web mobile-first é suficiente.

**O que fazemos**:
- ✅ Interface web mobile-first (responsive)
- ✅ App web para motorista (PWA - futuro MVP 3)
- ✅ App web para cliente B2B (PWA - futuro MVP 4)

---

### 8. Chatbot ou IA Conversacional

**Não fazemos**:
- ❌ Chatbot genérico
- ❌ Assistente virtual
- ❌ IA conversacional

**Por quê**: Não resolve problema real. Vendedor precisa criar cotação rápido, não conversar.

**O que fazemos**:
- ✅ Busca em tempo real (produtos, clientes)
- ✅ Sugestões inteligentes de reposição (MVP 2)
- ✅ Detecção de risco de ruptura (MVP 2)

---

## O Que Não É Prioridade (Futuro)

### 1. Integração com Transportadoras

**Não priorizamos** (MVP 1-3):
- ❌ Integração com transportadoras terceirizadas
- ❌ Rastreamento de envios
- ❌ Gestão de múltiplos transportadores

**Quando**: MVP 5+ (após validação de necessidade)

**Por quê**: Lojas geralmente têm motoristas próprios. Transportadora terceirizada é menos comum.

---

### 2. Pagamento Online

**Não priorizamos** (MVP 1-4):
- ❌ Integração com gateway de pagamento
- ❌ Pagamento via cartão/PIX online
- ❌ Gestão de pagamentos online

**Quando**: MVP 5+ (após validação de necessidade)

**Por quê**: Cliente B2B geralmente paga via boleto ou transferência manual. Pagamento online pode ser futuro.

---

### 3. Relatórios Avançados

**Não priorizamos** (MVP 1-2):
- ❌ Relatórios complexos (BI)
- ❌ Dashboards avançados
- ❌ Análise preditiva avançada

**Quando**: MVP 5+ (após validação de necessidade)

**Por quê**: Dashboard simples é suficiente inicialmente. Relatórios avançados podem ser futuro.

---

### 4. Multi-Idioma

**Não priorizamos** (MVP 1-5):
- ❌ Interface em múltiplos idiomas
- ❌ Tradução do sistema

**Quando**: Nunca (produto é regional)

**Por quê**: Produto é para região de Barra Mansa/Volta Redonda. Não há necessidade de multi-idioma.

---

### 5. Multi-Moeda

**Não priorizamos** (MVP 1-5):
- ❌ Suporte a múltiplas moedas
- ❌ Conversão de moeda

**Quando**: Nunca (produto é regional)

**Por quê**: Produto é para Brasil. Não há necessidade de multi-moeda.

---

## O Que Só Entra Após Validação

### 1. Novos Core Modules

**Validação necessária**:
- ✅ Há necessidade comprovada de reutilização?
- ✅ Problema é universal (não específico de vertical)?
- ✅ ROI de criar core module é positivo?
- ✅ Vertical inicial está validado?

**Exemplos**:
- **Pricing Intelligence Engine**: Só criar se houver necessidade de reutilização
- **Customer Intelligence Engine**: Só criar se houver necessidade de reutilização
- **Logistics Intelligence Engine**: Só criar se houver necessidade de reutilização

**Quando**: MVP 5+ (após validação)

**Observações**: Core modules são criados apenas quando há necessidade comprovada de reutilização. Não antecipar criação sem validação.

**Exceção**: Stock Intelligence Engine já está validado como necessário (MVP 2).

---

### 2. Integração Fiscal

**Validação necessária**:
- ✅ Cliente pediu integração fiscal?
- ✅ Qual sistema fiscal o cliente usa?
- ✅ Quantos clientes precisam disso?
- ✅ ROI da integração é positivo?

**Quando**: MVP 5+ (após validação)

**Observações**: Integração fiscal é complexa e cara. Só fazer se validado que é necessário.

---

### 3. App Mobile Nativo

**Validação necessária**:
- ✅ Cliente pediu app nativo?
- ✅ Web mobile não é suficiente?
- ✅ Quantos usuários precisam?
- ✅ ROI do app nativo é positivo?

**Quando**: MVP 5+ (após validação)

**Observações**: App nativo é caro. Web mobile-first deve ser suficiente. Só fazer se validado.

---

### 4. Portal B2C (Consumidor Final)

**Validação necessária**:
- ✅ Cliente pediu portal B2C?
- ✅ Quantos clientes B2C têm?
- ✅ ROI do portal B2C é positivo?

**Quando**: MVP 5+ (após validação)

**Observações**: Foco é B2B. Portal B2C só se validado que há demanda.

---

## O Que Nunca Será Objetivo

### 1. Ser um ERP Completo

**Nunca faremos**:
- ❌ Sistema completo de gestão empresarial
- ❌ Tudo em um sistema
- ❌ Competir com ERPs tradicionais (TOTVS, Senior, etc.)

**Por quê**: Não é nosso core. Somos especializados em cotações e pedidos para lojas de materiais de construção.

**O que somos**:
- ✅ SaaS vertical para lojas de materiais de construção
- ✅ Foco em cotações, pedidos, estoque e entrega
- ✅ Integração com sistemas existentes

---

### 2. Ser um Marketplace

**Nunca faremos**:
- ❌ Marketplace para comparar preços
- ❌ Conectar múltiplas lojas
- ❌ Intermediação entre lojas e clientes

**Por quê**: Não é nosso modelo de negócio. Cada loja é independente.

**O que somos**:
- ✅ Software para loja individual
- ✅ Cada loja gerencia seus próprios dados
- ✅ Isolamento total entre lojas

---

### 3. Ser um Sistema de Obra

**Nunca faremos**:
- ❌ Gestão de obras
- ❌ Cronograma de obras
- ❌ Controle de custos de obra

**Por quê**: É outro domínio. Obras são clientes, não é nosso core.

**O que fazemos**:
- ✅ Vendemos para obras (são clientes)
- ✅ Rastreamos entregas em obras
- ✅ Permitimos preços diferenciados por obra

---

### 4. Ser um Sistema de Transporte

**Nunca faremos**:
- ❌ Gestão de frota completa
- ❌ Roteirização complexa
- ❌ Sistema de transporte independente

**Por quê**: Foco é venda, não transporte. Transporte é meio, não fim.

**O que fazemos**:
- ✅ Roteirização simples (agrupamento por região)
- ✅ Prova de entrega
- ✅ Rastreamento básico de status

---

## Princípios de Decisão

### 1. Foco no Core

Se não é **cotações, pedidos, estoque ou entrega**, provavelmente não é nosso core.

### 2. Verticalização

Somos **especializados** em lojas de materiais de construção. Não tentamos ser genérico.

### 3. Integração, Não Substituição

**Integramos** com sistemas existentes (fiscal, financeiro). Não tentamos substituí-los.

### 4. Regional

Produto é para **Barra Mansa/Volta Redonda**. Não tentamos ser nacional ou internacional.

### 5. Validação Antes de Implementar

**Validação** antes de adicionar funcionalidades complexas ou caras.

---

## Quando Revisar Esta Lista

Revisar esta lista a cada:
- ✅ Fim de cada MVP
- ✅ Cliente pedir funcionalidade que está aqui
- ✅ Mudança de estratégia do produto

**Decisão**: Se cliente pedir algo que está nesta lista, deve ser **validado** antes de implementar. Não implementar automaticamente.

---

## Resumo

### Não Fazemos

1. Sistema fiscal completo
2. Gestão financeira completa
3. Gestão de obras
4. Marketplace
5. E-commerce B2C
6. Gestão de fornecedores
7. App mobile nativo (MVP 1-4)
8. Chatbot ou IA conversacional

### Não Priorizamos (Futuro)

1. Integração com transportadoras (MVP 5+)
2. Pagamento online (MVP 5+)
3. Relatórios avançados (MVP 5+)
4. Multi-idioma (nunca)
5. Multi-moeda (nunca)

### Só Após Validação

1. Integração fiscal (MVP 5+)
2. App mobile nativo (MVP 5+)
3. Portal B2C (MVP 5+)

### Nunca

1. ERP completo
2. Marketplace
3. Sistema de obra
4. Sistema de transporte

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

