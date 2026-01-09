# Fluxos Centrais do Sistema

## Visão Geral

Este documento descreve os fluxos principais do sistema passo a passo, em texto, sem diagramas gráficos. Cada fluxo representa uma jornada completa do usuário para alcançar um objetivo.

---

## Fluxo 1: Cotação

### Objetivo

Criar uma cotação rápida (3 minutos) e enviar para o cliente.

### Participantes

- **Vendedor**: Cria e envia a cotação
- **Cliente**: Recebe e aprova a cotação (futuro: aprova online)

### Passo a Passo

#### 1. Início

Vendedor clica em "Nova Cotação" no dashboard ou menu.

#### 2. Selecionar Cliente

- Vendedor busca cliente por nome, documento ou email
- Sistema mostra resultados em tempo real
- Se cliente não existe:
  - Vendedor clica "Novo Cliente"
  - Preenche dados básicos (nome, documento, contato)
  - Sistema cria cliente e seleciona automaticamente
- Vendedor seleciona cliente da lista

#### 3. Selecionar Obra (Opcional)

- Se cliente é PJ, sistema mostra obras do cliente
- Vendedor pode selecionar obra específica ou deixar em branco
- Se não há obra, vendedor pode criar nova obra ou pular

#### 4. Adicionar Produtos

- Vendedor busca produto por nome ou código
- Sistema mostra resultados em tempo real
- Vendedor clica "+" para adicionar produto à cotação
- Produto aparece na lista de itens com:
  - Quantidade padrão: 1
  - Preço unitário: preço base do produto
  - Desconto: 0%
- Vendedor ajusta:
  - Quantidade (ex: 10, 2.5, 100)
  - Preço unitário (se diferente do base)
  - Desconto percentual do item (ex: 5%)
- Sistema calcula valor total do item automaticamente

#### 5. Revisar Itens

- Vendedor vê lista de todos os itens adicionados
- Pode remover item clicando em "Remover"
- Pode editar quantidade, preço ou desconto
- Sistema calcula:
  - Subtotal (soma de todos os itens)
  - Desconto geral (percentual aplicado no subtotal)
  - Total final

#### 6. Aplicar Desconto Geral

- Vendedor pode aplicar desconto percentual geral na cotação
- Sistema recalcula total automaticamente
- Desconto geral é diferente do desconto por item

#### 7. Adicionar Observações

- Vendedor pode adicionar observações gerais (opcional)
- Exemplos: "Validade 7 dias", "Entrega na obra", "Pagamento à vista"

#### 8. Salvar ou Enviar

- **Salvar como Rascunho**:
  - Cotação fica com status "rascunho"
  - Pode ser editada depois
  - Não é enviada para cliente
- **Enviar Cotação**:
  - Cotação muda status para "enviada"
  - Futuro: sistema envia email com PDF
  - Atualmente: vendedor imprime ou envia via WhatsApp manualmente

#### 9. Finalização

- Cotação é salva
- Vendedor retorna ao dashboard ou lista de cotações
- Cotação aparece na lista com status "enviada"

### Regras de Negócio

- Cotação em rascunho pode ser editada
- Cotação enviada não pode ser editada (apenas visualizada)
- Cotação enviada pode ser aprovada (mudança manual de status) ou convertida em pedido
- Cotação aprovada pode ser convertida em pedido (1 clique)
- Cotação convertida não pode mais ser editada ou cancelada

### Tempo Estimado

- Objetivo: 3 minutos
- Com cliente existente: 2-3 minutos
- Com cliente novo: 3-5 minutos
- Com muitos produtos: 5-7 minutos

---

## Fluxo 2: Conversão em Pedido

### Objetivo

Converter cotação aprovada em pedido em 1 clique.

### Participantes

- **Vendedor** ou **Admin**: Converte cotação em pedido
- **Cliente**: Já aprovou a cotação (implicitamente ou explicitamente)

### Passo a Passo

#### 1. Visualizar Cotação Aprovada

- Usuário acessa lista de cotações
- Filtra por status "aprovada"
- Clica na cotação desejada

#### 2. Verificar Detalhes

- Usuário confirma:
  - Cliente está correto
  - Obra está correta (se houver)
  - Itens estão corretos
  - Total está correto

#### 3. Converter em Pedido

- Usuário clica em "Converter em Pedido"
- Sistema mostra modal de confirmação:
  - Número da cotação
  - Cliente
  - Total
  - Botão "Confirmar" e "Cancelar"
- Usuário clica "Confirmar"

#### 4. Processamento Automático

- Sistema cria pedido automaticamente:
  - Gera número único de pedido (ex: PED-001)
  - Copia todos os dados da cotação:
    - Cliente
    - Obra (se houver)
    - Todos os itens (produto, quantidade, preço, desconto)
    - Observações
  - Status inicial: "pendente"
  - Vincula pedido à cotação original
- Sistema atualiza cotação:
  - Status muda para "convertida"
  - Data de conversão registrada
  - Cotação não pode mais ser editada

#### 5. Finalização

- Usuário é redirecionado para detalhes do pedido
- Pedido aparece na lista de pedidos
- Cotação original mostra status "convertida" e link para pedido

### Regras de Negócio

- Apenas cotações aprovadas podem ser convertidas
- Cotação convertida não pode mais ser editada
- Pedido herda todos os dados da cotação (imutável)
- Preços são "congelados" no momento da cotação
- Um pedido pode ter apenas uma cotação origem
- Uma cotação pode gerar apenas um pedido (1:1)

### Tempo Estimado

- Objetivo: 1 clique (< 10 segundos)
- Realidade: 30 segundos (incluindo verificação)

---

## Fluxo 3: Entrega

### Objetivo

Entregar pedido na obra e registrar prova de entrega.

### Participantes

- **Motorista**: Entrega o pedido
- **Cliente** (responsável na obra): Recebe e assina

### Passo a Passo (MVP 1: Básico)

#### 1. Preparar Pedido

- Admin ou estoquista atualiza status do pedido para "em_preparacao"
- Itens são preparados fisicamente

#### 2. Atribuir para Entrega

- Admin atualiza status do pedido para "saiu_entrega"
- Anota motorista responsável (manual no MVP 1)
- Futuro: Sistema atribui motorista e rota

#### 3. Transporte

- Motorista leva pedido para obra
- Futuro: Sistema mostra rota no app do motorista

#### 4. Chegada na Obra

- Motorista chega na obra
- Futuro: Motorista marca "chegou" no app
- MVP 1: Manual (telefone ou WhatsApp)

#### 5. Entrega

- Motorista entrega produtos
- Responsável na obra confere itens
- Futuro: Sistema permite:
  - Foto dos produtos entregues
  - Assinatura digital do responsável
  - Observações de divergência
- MVP 1: Manual (papel ou WhatsApp)

#### 6. Finalização

- Admin atualiza status do pedido para "entregue"
- Data de entrega registrada
- Futuro: Prova de entrega (foto, assinatura) é salva automaticamente

### Passo a Passo (MVP 3: Completo)

#### 1. Preparar Pedido

- Sistema atualiza status automaticamente quando admin marca "em_preparacao"

#### 2. Roteirização

- Sistema agrupa pedidos por região/obra
- Sistema sugere rota otimizada
- Admin confirma rota

#### 3. Atribuir Motorista

- Sistema atribui rota para motorista
- Motorista recebe notificação no app
- Motorista confirma recebimento da rota

#### 4. Transporte

- Motorista vê rota no app
- Sistema rastreia localização (futuro: GPS)
- Sistema atualiza status automaticamente

#### 5. Chegada

- Motorista marca "chegou" no app quando chega na obra

#### 6. Entrega

- Motorista tira foto dos produtos entregues
- Responsável assina digitalmente no app do motorista
- Sistema permite registrar divergências (faltou item, item errado)
- Sistema registra observações

#### 7. Finalização Automática

- Sistema atualiza status para "entregue" automaticamente
- Data/hora de entrega registrada
- Prova de entrega (foto, assinatura) é salva
- Cliente recebe notificação (futuro)

### Regras de Negócio

- Pedido só pode ser marcado como "entregue" após sair para entrega
- Pedido entregue não pode ser cancelado
- Prova de entrega é obrigatória (MVP 3+)
- Divergências devem ser registradas (futuro)

### Tempo Estimado

- MVP 1: Manual (admin marca quando motorista avisa)
- MVP 3: Automático (motorista marca no app)

---

## Fluxo 4: Recompra

### Objetivo

Cliente faz novo pedido baseado em pedido anterior (recompra rápida).

### Participantes

- **Cliente B2B** (futuro: acessa e-commerce B2B)
- **Vendedor** (MVP 1-3: faz no balcão)

### Passo a Passo (MVP 1-3: Via Vendedor)

#### 1. Cliente Solicita Recompra

- Cliente liga ou vai na loja
- Diz: "Quero os mesmos produtos do pedido PED-045"

#### 2. Vendedor Busca Pedido Anterior

- Vendedor busca pedido pelo número ou cliente
- Sistema mostra pedido anterior

#### 3. Criar Nova Cotação ou Pedido

- Vendedor clica "Recomprar" ou "Duplicar"
- Sistema cria nova cotação ou pedido com:
  - Mesmos produtos
  - Mesmas quantidades
  - Preços atualizados (não "congelados")
- Vendedor ajusta:
  - Quantidades (se necessário)
  - Preços (se necessário)
  - Observações

#### 4. Finalizar

- Se cotação: vendedor envia para cliente
- Se pedido: vendedor confirma e marca para preparação

### Passo a Passo (MVP 4: Via E-commerce B2B)

#### 1. Cliente Acessa Portal

- Cliente faz login no portal B2B
- Sistema mostra catálogo personalizado (preços negociados)

#### 2. Ver Pedidos Anteriores

- Cliente acessa "Meus Pedidos"
- Vê lista de pedidos anteriores
- Clica no pedido desejado

#### 3. Recomprar

- Cliente clica "Recomprar"
- Sistema adiciona todos os itens do pedido ao carrinho
- Preços são atualizados (não "congelados")
- Quantidades são as mesmas

#### 4. Ajustar (Opcional)

- Cliente pode ajustar:
  - Quantidades
  - Remover itens
  - Adicionar novos itens

#### 5. Finalizar Pedido

- Cliente revisa carrinho
- Confirma pedido
- Sistema cria pedido automaticamente
- Cliente recebe confirmação

### Regras de Negócio

- Recompra usa preços atuais, não preços do pedido anterior
- Quantidades podem ser ajustadas
- Itens podem ser removidos ou adicionados
- Recompra pode gerar cotação ou pedido direto (depende do contexto)

### Tempo Estimado

- MVP 1-3 (via vendedor): 2-3 minutos
- MVP 4 (via cliente): 1-2 minutos

---

## Fluxo 5: Reposição de Estoque (MVP 2)

### Objetivo

Saber o que comprar e quando comprar para evitar ruptura e excesso, usando o Stock Intelligence Engine.

### Participantes

- **Estoquista** ou **Admin**: Analisa sugestões do engine e decide o que comprar
- **Stock Intelligence Engine (Core)**: Fornece alertas, sugestões e análises
- **Fornecedor**: Recebe pedido de compra

### Passo a Passo (MVP 2: Implementado)

#### 1. Módulo de Estoque Envia Dados para o Engine

- Módulo de Estoque envia histórico de vendas (via pedidos entregues) para o **Stock Intelligence Engine**
- Módulo de Estoque envia estoque atual (quantidade disponível) para o engine
- Módulo de Estoque configura parâmetros de reposição (lead time, estoque de segurança)

#### 2. Stock Intelligence Engine Analisa Vendas

- **Engine** analisa histórico de vendas por produto (genérico)
- **Engine** calcula:
  - Média de vendas por período (semana, mês)
  - Desvio padrão (variação)
  - Sazonalidade (se houver, simples)

#### 3. Stock Intelligence Engine Classifica Produtos (Curva ABC)

- **Engine** classifica produtos em:
  - **Classe A**: Alto giro (20% dos produtos = 80% das vendas)
  - **Classe B**: Médio giro
  - **Classe C**: Baixo giro (80% dos produtos = 20% das vendas)
- **Engine** retorna análise ABC para o módulo vertical

#### 4. Stock Intelligence Engine Calcula Estoque Mínimo/Máximo

- **Engine** calcula para cada produto:
  - Estoque mínimo = (média vendas × tempo de reposição) + segurança
  - Estoque máximo = (média vendas × tempo de reposição × 2)
- **Engine** retorna cálculos para o módulo vertical

#### 5. Stock Intelligence Engine Detecta Risco de Ruptura

- **Engine** compara estoque atual com estoque mínimo calculado
- Produtos abaixo do mínimo = risco de ruptura
- **Engine** gera alerta com explicação em linguagem natural
- **Engine** retorna alertas para o módulo vertical

#### 6. Stock Intelligence Engine Sugere Reposição

- **Engine** sugere:
  - Produtos a comprar (abaixo do mínimo)
  - Quantidade sugerida (estoque máximo - estoque atual)
  - Prioridade (Classe A = alta prioridade)
  - Explicação em linguagem natural (ex: "Vende 10 unidades/dia, lead time 7 dias, sugere 100 unidades")
- **Engine** retorna sugestões para o módulo vertical

#### 6. Usuário Analisa e Decide

- Estoquista ou admin visualiza sugestões
- Ajusta quantidades se necessário
- Remove produtos se não quiser comprar
- Adiciona produtos se necessário

#### 7. Módulo Vertical Apresenta Sugestões para Usuário

- Módulo de Estoque apresenta alertas e sugestões do engine para usuário
- Usuário visualiza:
  - Alertas de risco de ruptura (do engine)
  - Sugestões de reposição (do engine)
  - Análise ABC (do engine)
  - Explicações em linguagem natural (do engine)
- Interface é específica do vertical (ex: "Comprar cimento para obra X")

#### 8. Usuário Analisa e Decide

- Estoquista ou admin analisa sugestões do engine
- Ajusta quantidades se necessário (vertical permite ajuste)
- Remove produtos se não quiser comprar
- Adiciona produtos se necessário

#### 9. Gerar Lista de Compras (Vertical)

- Módulo vertical gera lista de compras baseada em decisão do usuário
- Lista é específica do vertical (formato, produtos, etc.)
- Usuário envia para fornecedor (futuro: integração automática)

#### 10. Atualizar Estoque Após Recebimento (Vertical)

- Quando produtos chegam do fornecedor:
- Estoquista atualiza estoque físico no módulo vertical
- Módulo vertical registra movimentação
- Próximo ciclo: Módulo envia estoque atualizado para o engine novamente

### Regras de Negócio

**Stock Intelligence Engine (Core)**:
- Estoque mínimo = proteção contra ruptura (calculado pelo engine)
- Estoque máximo = limite de capital parado (calculado pelo engine)
- Curva ABC = foco no que vende mais (calculado pelo engine)
- Sazonalidade = ajuste para períodos de maior/menor venda (detectado pelo engine)
- Tempo de reposição = lead time do fornecedor (configurado pelo vertical)

**Módulo de Estoque (Vertical)**:
- Decisão final de compra é do usuário (vertical não decide sozinho)
- Gestão de estoque físico é responsabilidade do vertical (entradas/saídas)
- Interpretação de sugestões é responsabilidade do vertical (contexto específico)

### Tempo Estimado

- MVP 1: Manual (admin decide baseado em feeling)
- MVP 2: Semi-automático (engine sugere, admin decide via módulo vertical)
- Futuro: Automático (módulo vertical gera ordem de compra baseada em sugestões do engine)

### Observações

- **Engine não decide**: Engine apenas sugere, usuário decide
- **Vertical interpreta**: Vertical apresenta sugestões do engine no contexto de materiais de construção
- **Separação clara**: Engine fornece inteligência (o que fazer), Vertical executa (como fazer)

---

## Fluxos Secundários

### Fluxo: Cancelar Cotação

1. Usuário acessa cotação
2. Clica "Cancelar"
3. Sistema marca status como "cancelada"
4. Cotação cancelada não pode ser editada ou convertida

### Fluxo: Cancelar Pedido

1. Admin acessa pedido
2. Verifica se pode cancelar (não entregue)
3. Clica "Cancelar"
4. Sistema marca status como "cancelado"
5. Pedido cancelado não pode ser reativado

### Fluxo: Editar Produto

1. Admin acessa produto
2. Altera preço, descrição, etc.
3. Sistema salva alteração
4. Sistema registra no histórico de preços (se preço mudou)
5. Preços em cotações/pedidos existentes não mudam (congelados)

### Fluxo: Criar Cliente

1. Vendedor ou admin busca cliente
2. Cliente não existe
3. Clica "Novo Cliente"
4. Preenche dados básicos
5. Sistema valida documento único por loja
6. Sistema cria cliente
7. Cliente fica disponível para uso

---

## Observações Gerais

### 1. Imutabilidade

- Pedidos são imutáveis após criação (apenas status muda)
- Cotações convertidas são imutáveis
- Preços em itens são "congelados" no momento da criação

### 2. Versionamento

- Preços têm histórico
- Cotações preservam estado mesmo após conversão
- Mudanças são registradas com usuário e data

### 3. Validações

- Cliente deve existir antes de criar cotação
- Produto deve estar ativo para adicionar na cotação
- Cotação deve ter pelo menos 1 item
- Pedido deve ter pelo menos 1 item

### 4. Permissões

- Vendedor cria e envia cotações
- Admin aprova e converte
- Financeiro aprova (após compromisso/pagamento)
- Motorista marca entrega (MVP 3+)

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

