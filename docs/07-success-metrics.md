# Métricas de Sucesso

## Visão Geral

Este documento define métricas claras e mensuráveis para avaliar o sucesso do produto em diferentes dimensões: produto, operação, financeiro, adoção e retenção.

---

## Métricas de Produto

### 1. Tempo Médio de Cotação

**Definição**: Tempo médio que um vendedor leva para criar uma cotação completa (do início até salvar/enviar).

**Como medir**: Timestamp de criação vs timestamp de envio/salvamento. Calcular média das últimas 30 cotações.

**Meta MVP 1**: 3-5 minutos

**Baseline atual**: 15-20 minutos (manual)

**Valor alvo**: 3 minutos

**Como melhorar**:
- Busca em tempo real (produtos, clientes)
- Interface otimizada (poucos cliques)
- Autocomplete e sugestões
- Preenchimento automático (cliente, obra)

---

### 2. Taxa de Conversão Cotação → Pedido

**Definição**: Porcentagem de cotações aprovadas que são convertidas em pedidos.

**Como medir**: (Cotações convertidas / Cotações aprovadas) × 100

**Meta MVP 1**: 60%+

**Baseline atual**: ~30% (manual)

**Valor alvo**: 70%+

**Como melhorar**:
- Conversão em 1 clique
- Lembrete para converter
- Notificação quando cotação é aprovada
- Histórico de conversões

---

### 3. Taxa de Erro em Cotações

**Definição**: Porcentagem de cotações que têm erro (preço errado, quantidade errada, produto errado).

**Como medir**: (Cotações com erro / Total de cotações) × 100. Erro detectado via reclamação do cliente ou edição após envio.

**Meta MVP 1**: <5%

**Baseline atual**: ~15% (manual)

**Valor alvo**: <3%

**Como melhorar**:
- Validação em tempo real
- Confirmação antes de enviar
- Histórico de preços
- Busca eficiente (menos erro de digitação)

---

### 4. Taxa de Erro em Pedidos

**Definição**: Porcentagem de pedidos que têm erro (diferença entre cotação e pedido, item faltando, quantidade errada).

**Como medir**: (Pedidos com erro / Total de pedidos) × 100. Erro detectado via reclamação do cliente ou divergência na entrega.

**Meta MVP 1**: <5%

**Baseline atual**: ~15% (manual)

**Valor alvo**: <3%

**Como melhorar**:
- Conversão automática (copia dados da cotação)
- Validação antes de criar pedido
- Confirmação visual
- Não permite editar pedido após criação

---

## Métricas de Operação

### 5. Ruptura de Estoque

**Definição**: Porcentagem de itens que ficaram em ruptura (estoque zero) em um período.

**Como medir**: (Itens em ruptura / Total de itens ativos) × 100. Calcular para últimos 30 dias.

**Meta MVP 2**: <5%

**Baseline atual**: ~20% (manual)

**Valor alvo**: <3%

**Como melhorar**:
- **Stock Intelligence Engine**: Sugestão de reposição e alertas de risco de ruptura
- **Módulo de Estoque**: Gestão física e apresentação de alertas para usuário
- **Stock Intelligence Engine**: Curva ABC (foco no que vende mais)
- **Stock Intelligence Engine**: Histórico de vendas analisado pelo engine

**Observação**: Métrica é do resultado final (vertical), mas depende do engine para alcançar meta.

---

### 6. Capital Parado em Estoque

**Definição**: Porcentagem do capital investido em estoque que está parado (produtos que não vendem ou vendem pouco).

**Como medir**: (Valor de estoque parado / Valor total de estoque) × 100. Estoque parado = itens com giro < X por período (ex: 0 vendas nos últimos 60 dias).

**Meta MVP 2**: <30%

**Baseline atual**: 40-50% (manual)

**Valor alvo**: <25%

**Como melhorar**:
- **Stock Intelligence Engine**: Sugestão de reposição baseada em vendas históricas
- **Stock Intelligence Engine**: Curva ABC (foco no que vende)
- **Stock Intelligence Engine**: Alertas de estoque acima do máximo sugerido
- **Módulo de Estoque**: Relatório de itens parados (usando dados do engine)

**Observação**: Métrica é do resultado final (vertical), mas depende do engine para alcançar meta.

---

### 7. Tempo Médio de Entrega

**Definição**: Tempo médio entre criação do pedido e entrega (em dias).

**Como medir**: (Data de entrega - Data de criação do pedido). Calcular média dos últimos 30 pedidos entregues.

**Meta MVP 3**: 1-2 dias

**Baseline atual**: 3-5 dias (manual)

**Valor alvo**: 1 dia

**Como melhorar**:
- Roteirização (MVP 3)
- Planejamento de entregas
- Otimização de rotas
- Comunicação com cliente

---

### 8. Taxa de Erro na Entrega

**Definição**: Porcentagem de entregas que têm erro (item faltando, item errado, quantidade errada).

**Como medir**: (Entregas com erro / Total de entregas) × 100. Erro detectado via divergência registrada ou reclamação.

**Meta MVP 3**: <3%

**Baseline atual**: ~10% (manual)

**Valor alvo**: <2%

**Como melhorar**:
- Prova de entrega (foto, assinatura) (MVP 3)
- Conferência antes de sair
- Lista de itens para entregador
- Registro de divergências

---

### 9. Taxa de Conflito (Reclamação)

**Definição**: Porcentagem de entregas que resultam em reclamação do cliente.

**Como medir**: (Entregas com reclamação / Total de entregas) × 100. Reclamação registrada no sistema ou via contato.

**Meta MVP 3**: <5%

**Baseline atual**: ~15% (manual)

**Valor alvo**: <3%

**Como melhorar**:
- Prova de entrega (foto, assinatura) (MVP 3)
- Registro de divergências
- Comunicação proativa
- Resolução rápida

---

## Métricas Financeiras

### 10. Receita Recorrente Mensal (MRR)

**Definição**: Receita mensal recorrente de assinaturas.

**Como medir**: Soma de todas as assinaturas mensais ativas.

**Meta MVP 1**: R$ 10.000/mês (10 lojas × R$ 1.000/mês)

**Meta MVP 2**: R$ 50.000/mês (50 lojas × R$ 1.000/mês)

**Valor alvo**: R$ 100.000/mês (100 lojas)

**Como melhorar**:
- Aumentar número de clientes
- Aumentar preço (se valor justificado)
- Upsell de módulos adicionais

---

### 11. Lifetime Value (LTV)

**Definição**: Valor total que um cliente gera ao longo do relacionamento.

**Como medir**: (Receita média por mês × Tempo médio de permanência). Ou: (Preço mensal × Número de meses médio).

**Meta MVP 1**: R$ 12.000 (R$ 1.000/mês × 12 meses)

**Valor alvo**: R$ 24.000+ (R$ 1.000/mês × 24+ meses)

**Como melhorar**:
- Aumentar retenção (clientes ficam mais tempo)
- Upsell de módulos
- Aumentar preço (se valor justificado)

---

### 12. Customer Acquisition Cost (CAC)

**Definição**: Custo médio para adquirir um cliente.

**Como medir**: (Custo de marketing + Vendas + Onboarding) / Número de clientes adquiridos.

**Meta MVP 1**: R$ 2.000 por cliente

**Valor alvo**: R$ 1.500 por cliente

**Como melhorar**:
- Reduzir custo de aquisição (marketing eficiente)
- Aumentar conversão (vendas)
- Referral (clientes indicam clientes)

---

### 13. LTV:CAC Ratio

**Definição**: Razão entre Lifetime Value e Customer Acquisition Cost.

**Como medir**: LTV / CAC

**Meta MVP 1**: 6:1 (R$ 12.000 / R$ 2.000)

**Valor alvo**: 10:1+ (R$ 24.000 / R$ 1.500 = 16:1)

**Como melhorar**:
- Aumentar LTV (retenção, upsell)
- Reduzir CAC (aquisição eficiente)

---

## Métricas de Adoção

### 14. Taxa de Adoção do Portal B2B

**Definição**: Porcentagem de clientes B2B que usam o portal (fazem pedidos via portal).

**Como medir**: (Clientes B2B que usam portal / Total de clientes B2B) × 100.

**Meta MVP 4**: 50%+

**Valor alvo**: 70%+

**Como melhorar**:
- Portal simples e intuitivo
- Onboarding para clientes
- Demonstração de valor
- Suporte próximo

---

### 15. Taxa de Recompra via Portal

**Definição**: Porcentagem de pedidos feitos via portal (vs balcão).

**Como medir**: (Pedidos via portal / Total de pedidos) × 100.

**Meta MVP 4**: 30%+

**Valor alvo**: 50%+

**Como melhorar**:
- Recompra rápida (duplicar pedido)
- Catálogo personalizado
- Preços negociados
- Interface mobile-friendly

---

### 16. Número de Clientes Ativos

**Definição**: Número de lojas que usam o sistema ativamente (fazem pelo menos 1 cotação/pedido por mês).

**Como medir**: Contar lojas com pelo menos 1 cotação/pedido nos últimos 30 dias.

**Meta MVP 1**: 10 lojas (6 meses)

**Meta MVP 2**: 50 lojas (12 meses)

**Valor alvo**: 100+ lojas (24 meses)

**Como melhorar**:
- Aquisição de clientes
- Retenção (clientes continuam usando)
- Expansão (lojas adotam mais módulos)

---

## Métricas de Retenção

### 17. Taxa de Retenção (Churn Rate)

**Definição**: Porcentagem de clientes que cancelam a assinatura por mês.

**Como medir**: (Clientes que cancelaram no mês / Total de clientes no início do mês) × 100.

**Meta MVP 1**: <5% por mês

**Valor alvo**: <3% por mês

**Como melhorar**:
- Valor percebido (ROI claro)
- Suporte próximo
- Funcionalidades que resolvem problema
- Comunicação proativa

---

### 18. Taxa de Expansão (Upsell)

**Definição**: Porcentagem de clientes que adotam módulos adicionais (ex: estoque, logística).

**Como medir**: (Clientes com 2+ módulos / Total de clientes) × 100.

**Meta MVP 2**: 30%+ adotam módulo de estoque

**Meta MVP 3**: 20%+ adotam módulo de logística

**Valor alvo**: 50%+ adotam 2+ módulos

**Como melhorar**:
- Demonstrar valor de cada módulo
- Integração natural entre módulos
- Preço justo
- Casos de sucesso

---

### 19. Net Promoter Score (NPS)

**Definição**: Medida de satisfação e lealdade do cliente (0-10).

**Como medir**: Perguntar: "Em uma escala de 0 a 10, qual a probabilidade de você recomendar este produto?". NPS = % Promotores (9-10) - % Detratores (0-6).

**Meta MVP 1**: 50+

**Valor alvo**: 70+

**Como melhorar**:
- Valor percebido (ROI)
- Suporte próximo
- Funcionalidades que resolvem problema
- Escutar feedback e ajustar

---

### 20. Satisfação do Vendedor

**Definição**: Medida de satisfação dos vendedores que usam o sistema (0-10).

**Como medir**: Pesquisa com vendedores: "Em uma escala de 0 a 10, como você avalia o sistema?".

**Meta MVP 1**: 7+ (média)

**Valor alvo**: 8+ (média)

**Como melhorar**:
- Interface simples e intuitiva
- Reduzir tempo de criação de cotação
- Busca eficiente
- Suporte próximo

---

## Dashboard de Métricas

### Visão Executiva

| Métrica | Meta MVP 1 | Valor Atual | Status |
|---------|------------|-------------|--------|
| Tempo médio de cotação | 3-5 min | 15-20 min | 🔴 |
| Taxa conversão cotação → pedido | 60%+ | ~30% | 🔴 |
| Taxa erro em pedidos | <5% | ~15% | 🔴 |
| Ruptura de estoque | <5% | ~20% | 🔴 |
| Capital parado | <30% | 40-50% | 🔴 |
| Tempo médio entrega | 1-2 dias | 3-5 dias | 🔴 |
| Taxa erro entrega | <3% | ~10% | 🔴 |
| MRR | R$ 10k/mês | R$ 0 | 🔴 |
| Clientes ativos | 10 lojas | 0 | 🔴 |
| Taxa retenção | <5%/mês | N/A | ⚪ |
| NPS | 50+ | N/A | ⚪ |

**Legenda**: 🔴 = Não alcançado, 🟡 = Parcialmente alcançado, 🟢 = Alcançado, ⚪ = Não medido ainda

---

## Como Medir

### 1. Métricas Automáticas

- Tempo médio de cotação (logs do sistema)
- Taxa de conversão (banco de dados)
- Taxa de erro (banco de dados + reclamações)
- Ruptura de estoque (banco de dados - MVP 2)
- Capital parado (banco de dados - MVP 2)
- Tempo médio de entrega (banco de dados - MVP 3)
- MRR (sistema de cobrança)
- Clientes ativos (banco de dados)

### 2. Métricas Manuais

- Taxa de erro (via reclamações)
- Taxa de conflito (via reclamações)
- Satisfação do vendedor (pesquisa)
- NPS (pesquisa)
- CAC (contabilidade)

### 3. Frequência de Medição

- **Diária**: Tempo médio de cotação, taxa de conversão, taxa de erro
- **Semanal**: Ruptura de estoque, capital parado, tempo médio de entrega
- **Mensal**: MRR, clientes ativos, taxa de retenção, NPS, satisfação

---

## Ações Baseadas em Métricas

### Se Tempo Médio de Cotação > 5 minutos

- ✅ Analisar logs (onde está demorando?)
- ✅ Simplificar interface
- ✅ Melhorar busca
- ✅ Adicionar autocomplete

### Se Taxa de Conversão < 50%

- ✅ Verificar se cotação está sendo enviada
- ✅ Lembrete para converter
- ✅ Facilitar conversão (1 clique)
- ✅ Notificação quando aprovada

### Se Taxa de Erro > 5%

- ✅ Validar em tempo real
- ✅ Confirmação antes de enviar
- ✅ Histórico de preços
- ✅ Busca eficiente

### Se Ruptura > 5% (MVP 2)

- ✅ **Stock Intelligence Engine**: Melhorar algoritmo de sugestão de reposição
- ✅ **Stock Intelligence Engine**: Alertas mais proativos (reduzir threshold)
- ✅ **Módulo de Estoque**: Ajustar parâmetros de reposição (lead time, segurança) enviados ao engine
- ✅ **Stock Intelligence Engine**: Focar em itens classe A (prioridade na análise ABC)

### Se Churn > 5%

- ✅ Entrevista com clientes que cancelaram
- ✅ Identificar problemas
- ✅ Ajustar produto ou suporte
- ✅ Programa de retenção

---

## Observações

### 1. Baseline Atual

Métricas baseline são estimativas baseadas em operação manual típica. Validação real deve ser feita ao medir primeiro cliente.

### 2. Evolução das Metas

Metas evoluem conforme MVP:
- MVP 1: Foco em cotações e pedidos
- MVP 2: Adiciona estoque
- MVP 3: Adiciona logística
- MVP 4: Adiciona e-commerce B2B

### 3. Métricas Não Medidas

Algumas métricas não podem ser medidas no MVP 1 (ex: ruptura de estoque sem módulo de estoque). Devem ser medidas quando módulo for implementado.

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

