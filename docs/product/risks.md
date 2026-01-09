# Assunções e Riscos

## Visão Geral

Este documento lista as **assunções** do negócio e os **riscos** técnicos, de adoção e regionais do sistema. É importante documentar para mitigar riscos e validar assunções.

---

## Assunções do Negócio

### 1. Clientes Têm Conexão com Internet

**Assunção**: Todas as lojas têm conexão com internet estável para usar o sistema.

**Validação**: Verificar antes de vender. Se loja não tem internet, não pode usar sistema SaaS.

**Mitigação**: Oferecer modo offline (futuro) ou instalação local (não SaaS).

**Impacto**: Alto - sem internet, sistema não funciona.

---

### 2. Vendedores Têm Dispositivo (Computador/Tablet)

**Assunção**: Vendedores têm acesso a computador ou tablet no balcão para usar o sistema.

**Validação**: Verificar antes de vender. Se não tem dispositivo, não pode usar sistema.

**Mitigação**: Sistema funciona em tablets e smartphones (mobile-first).

**Impacto**: Alto - sem dispositivo, vendedor não pode usar.

---

### 3. Cliente Quer Reduzir Retrabalho

**Assunção**: Cliente quer reduzir retrabalho na cotação e aumentar eficiência.

**Validação**: Validar em vendas. Se cliente não vê valor, não compra.

**Mitigação**: Demonstrar ROI claro (redução de retrabalho = economia de tempo = economia de dinheiro).

**Impacto**: Alto - sem valor percebido, cliente não adota.

---

### 4. Operação Atual é Manual

**Assunção**: Operação atual é manual (WhatsApp, planilha) e ineficiente.

**Validação**: Validar em vendas. Se operação já é eficiente, não há problema para resolver.

**Mitigação**: Identificar dor específica do cliente antes de vender.

**Impacto**: Médio - se operação já é eficiente, valor é menor.

---

### 5. Cliente Tem Múltiplos Vendedores

**Assunção**: Cliente tem 3+ vendedores e precisa de coordenação.

**Validação**: Verificar antes de vender. Se tem 1 vendedor, valor é menor.

**Mitigação**: Oferecer plano básico para lojas pequenas ou ajustar proposta de valor.

**Impacto**: Médio - se tem 1 vendedor, coordenação é menos crítica.

---

### 6. Preço Negociado é Importante

**Assunção**: Preço varia por cliente e obra, e negociar preço é importante.

**Validação**: Validar em vendas. Se preço é fixo, funcionalidade é menos crítica.

**Mitigação**: Ajustar proposta de valor ou priorizar outras funcionalidades.

**Impacto**: Baixo - preço negociado é importante, mas não crítico para MVP 1.

---

## Riscos Técnicos

### 1. Performance com Muitos Dados

**Risco**: Sistema pode ficar lento quando tem muitos produtos, clientes ou pedidos.

**Probabilidade**: Média (3-5 anos)

**Impacto**: Alto - se sistema fica lento, usuário desiste.

**Mitigação**:
- ✅ Indexar banco de dados corretamente
- ✅ Paginação e busca eficiente
- ✅ Cache de dados frequentes
- ✅ Otimização de queries
- ✅ Monitoramento de performance

---

### 2. Escalabilidade Multi-tenant

**Risco**: Sistema pode não escalar bem com muitos tenants (lojas).

**Probabilidade**: Média (2-3 anos)

**Impacto**: Alto - se não escala, não pode crescer.

**Mitigação**:
- ✅ Arquitetura multi-tenant desde início
- ✅ Isolamento de dados por tenant_id
- ✅ Sharding de banco de dados (futuro)
- ✅ Load balancing e caching
- ✅ Monitoramento de uso por tenant

---

### 3. Segurança de Dados

**Risco**: Dados podem ser comprometidos (hack, vazamento).

**Probabilidade**: Baixa (mas crítico)

**Impacto**: Crítico - vazamento de dados é grave.

**Mitigação**:
- ✅ Isolamento de dados por tenant
- ✅ Autenticação forte (JWT)
- ✅ HTTPS sempre
- ✅ Backup automático
- ✅ Criptografia de dados sensíveis
- ✅ Auditoria de acesso

---

### 4. Integração com Sistemas Externos

**Risco**: Integração com sistemas fiscais/financeiros pode ser complexa ou instável.

**Probabilidade**: Alta (quando implementar)

**Impacto**: Médio - integração é importante mas não crítica para MVP 1-3.

**Mitigação**:
- ✅ Validar necessidade antes de implementar
- ✅ Usar APIs estáveis
- ✅ Tratamento de erro robusto
- ✅ Modo degradado (sistema funciona sem integração)
- ✅ Testes de integração

---

### 5. Dependência de Terceiros

**Risco**: Dependências (bibliotecas, serviços) podem quebrar ou ficar desatualizadas.

**Probabilidade**: Média

**Impacto**: Médio - se dependência quebra, sistema pode quebrar.

**Mitigação**:
- ✅ Usar dependências estáveis e mantidas
- ✅ Versionar dependências
- ✅ Testes automatizados
- ✅ Monitoramento de vulnerabilidades
- ✅ Plano de migração

---

### 6. Acoplamento Entre Core e Vertical Modules

**Risco**: Core modules podem ficar acoplados a vertical específico, perdendo reutilização.

**Probabilidade**: Média (se não for cuidadoso)

**Impacto**: Alto - se core module fica acoplado, não pode ser reutilizado por outros verticais.

**Mitigação**:
- ✅ **Separação clara**: Core module não conhece vertical, apenas fornece inteligência genérica
- ✅ **API genérica**: Interface genérica não específica de vertical
- ✅ **Isolamento de responsabilidades**: Core fornece inteligência, vertical executa e interpreta
- ✅ **Validação**: Revisar código do core module para garantir que não há lógica específica de vertical
- ✅ **Documentação**: Documentar claramente o que é core vs vertical

**Observações**: Stock Intelligence Engine deve permanecer horizontal. Não pode ter conhecimento sobre "cimento" ou "leite".

---

### 7. Expansão Prematura de Core Modules

**Risco**: Criar core modules antes de validar necessidade de reutilização.

**Probabilidade**: Média (tentação de criar "genérico" antes de validar)

**Impacto**: Médio - recursos gastos em core module que pode não ser reutilizado.

**Mitigação**:
- ✅ **Validação antes**: Core module só é criado quando há necessidade comprovada de reutilização
- ✅ **Vertical primeiro**: Validar vertical inicial antes de criar core modules
- ✅ **Exceção**: Stock Intelligence Engine já está validado como necessário (MVP 2)
- ✅ **Documentação**: Documentar necessidade de reutilização antes de criar

**Observações**: Não antecipar criação de core modules. Priorizar vertical inicial.

---

## Riscos de Adoção

### 1. Resistência à Mudança

**Risco**: Vendedores podem resistir a mudar processo manual para sistema.

**Probabilidade**: Alta

**Impacto**: Alto - se vendedores não usam, sistema não funciona.

**Mitigação**:
- ✅ Treinamento adequado
- ✅ Interface simples e intuitiva
- ✅ Suporte próximo (primeiras semanas)
- ✅ Demonstrar valor (economia de tempo)
- ✅ Escutar feedback e ajustar

---

### 2. Curva de Aprendizado

**Risco**: Sistema pode ser difícil de aprender e vendedores podem desistir.

**Probabilidade**: Média

**Impacto**: Alto - se é difícil, vendedores não usam.

**Mitigação**:
- ✅ Interface desktop-first (familiar)
- ✅ Fluxo simples (criação em 3 minutos)
- ✅ Busca em tempo real (familiar)
- ✅ Tutorial/onboarding
- ✅ Suporte disponível

---

### 3. Falta de Suporte

**Risco**: Cliente pode não ter suporte quando precisa.

**Probabilidade**: Baixa (mas crítico)

**Impacto**: Alto - se não tem suporte, cliente desiste.

**Mitigação**:
- ✅ Suporte por WhatsApp/email
- ✅ Documentação clara
- ✅ FAQs
- ✅ Vídeos tutoriais
- ✅ Suporte dedicado (primeiras semanas)

---

### 4. Custo Percebido vs Valor

**Risco**: Cliente pode achar caro e não ver valor.

**Probabilidade**: Média

**Impacto**: Alto - se não vê valor, não paga.

**Mitigação**:
- ✅ Demonstrar ROI claro (redução de retrabalho)
- ✅ Plano de preços justo
- ✅ Período de teste gratuito
- ✅ Casos de sucesso
- ✅ Métricas de valor (tempo economizado, erro reduzido)

---

### 5. Dependência do Sistema

**Risco**: Cliente pode ficar dependente do sistema e ter problema se sistema cai.

**Probabilidade**: Baixa (mas crítico)

**Impacto**: Crítico - se sistema cai e cliente não consegue trabalhar, perde confiança.

**Mitigação**:
- ✅ Alta disponibilidade (99.9%+)
- ✅ Backup automático
- ✅ Modo degradado (funcionalidades críticas funcionam offline - futuro)
- ✅ Comunicação transparente em caso de problema
- ✅ Plano de contingência

---

## Riscos Regionais (Brasil)

### 1. Regulamentação Fiscal

**Risco**: Mudanças na legislação fiscal podem exigir mudanças no sistema.

**Probabilidade**: Média

**Impacto**: Médio - se muda legislação e sistema não acompanha, cliente pode precisar migrar.

**Mitigação**:
- ✅ Não fazer sistema fiscal (integração com sistemas especializados)
- ✅ Acompanhar mudanças legislativas
- ✅ Flexibilidade para ajustar

---

### 2. Complexidade Fiscal Brasileira

**Risco**: Sistema fiscal brasileiro é complexo e pode ser difícil integrar.

**Probabilidade**: Alta (quando implementar)

**Impacto**: Médio - integração fiscal é importante mas não crítica para MVP 1-3.

**Mitigação**:
- ✅ Validar necessidade antes de implementar
- ✅ Usar sistemas especializados (TOTVS, Senior, etc.)
- ✅ Integração via API, não tentar fazer tudo

---

### 3. Região Específica (Barra Mansa/Volta Redonda)

**Risco**: Produto pode não funcionar em outras regiões (diferenças regionais).

**Probabilidade**: Média (quando expandir)

**Impacto**: Baixo para MVP 1 (produto é regional), Alto se expandir.

**Mitigação**:
- ✅ Validar em outras regiões antes de expandir
- ✅ Flexibilidade para ajustar (preços, regras)
- ✅ Acompanhar feedback de clientes

---

### 4. Infraestrutura de Internet

**Risco**: Internet pode ser instável em algumas regiões (Barra Mansa/Volta Redonda).

**Probabilidade**: Baixa (mas possível)

**Impacto**: Médio - se internet cai, sistema não funciona.

**Mitigação**:
- ✅ Sistema funciona offline parcialmente (futuro)
- ✅ Sincronização quando internet volta
- ✅ Validação antes de vender (verificar conexão)

---

### 5. Logística Regional

**Risco**: Logística pode ser diferente em outras regiões (rotas, motoristas, etc.).

**Probabilidade**: Baixa (quando expandir)

**Impacto**: Baixo para MVP 1 (produto é regional), Médio se expandir.

**Mitigação**:
- ✅ Roteirização simples e flexível
- ✅ Acompanhar feedback de clientes
- ✅ Ajustar para região específica

---

## Riscos de Negócio

### 1. Competição

**Risco**: Concorrentes podem entrar no mercado ou oferecer solução similar.

**Probabilidade**: Média

**Impacto**: Médio - competição é normal, mas pode afetar crescimento.

**Mitigação**:
- ✅ Diferencial competitivo claro (verticalização)
- ✅ Foco em qualidade e suporte
- ✅ Inovação contínua
- ✅ Relacionamento próximo com clientes

---

### 2. Mudança de Prioridades

**Risco**: Prioridades podem mudar e recursos podem ser desviados.

**Probabilidade**: Baixa

**Impacto**: Médio - se prioridades mudam, roadmap pode atrasar.

**Mitigação**:
- ✅ Documentação clara de objetivos (este documento)
- ✅ Foco no core (cotações, pedidos, estoque, entrega)
- ✅ Revisão periódica de prioridades

---

### 3. Tecnologia Obsoleta

**Risco**: Tecnologia escolhida pode ficar obsoleta rapidamente.

**Probabilidade**: Baixa

**Impacto**: Baixo - tecnologias escolhidas são estáveis e mantidas.

**Mitigação**:
- ✅ Usar tecnologias estabelecidas (FastAPI, React, PostgreSQL)
- ✅ Arquitetura modular (fácil migrar partes)
- ✅ Acompanhar evolução tecnológica

---

## Matriz de Riscos

| Risco | Probabilidade | Impacto | Prioridade | Mitigação |
|-------|---------------|---------|------------|-----------|
| **Técnicos** |
| Performance com muitos dados | Média | Alto | Alta | ✅ Otimização, cache, monitoramento |
| Escalabilidade multi-tenant | Média | Alto | Alta | ✅ Arquitetura, sharding, monitoramento |
| Segurança de dados | Baixa | Crítico | Crítica | ✅ Isolamento, HTTPS, backup, auditoria |
| Integração com sistemas externos | Alta | Médio | Média | ✅ Validação, modo degradado, testes |
| Dependência de terceiros | Média | Médio | Média | ✅ Dependências estáveis, versionamento |
| Acoplamento Core vs Vertical | Média | Alto | Alta | ✅ Separação clara, API genérica, isolamento |
| Expansão prematura de Core | Média | Médio | Média | ✅ Validação antes, vertical primeiro |
| **Adoção** |
| Resistência à mudança | Alta | Alto | Alta | ✅ Treinamento, interface simples, suporte |
| Curva de aprendizado | Média | Alto | Alta | ✅ Interface intuitiva, tutorial, suporte |
| Falta de suporte | Baixa | Alto | Alta | ✅ Suporte disponível, documentação |
| Custo vs valor | Média | Alto | Alta | ✅ ROI claro, preço justo, teste gratuito |
| Dependência do sistema | Baixa | Crítico | Crítica | ✅ Alta disponibilidade, backup, comunicação |
| **Regionais** |
| Regulamentação fiscal | Média | Médio | Baixa | ✅ Não fazer sistema fiscal, flexibilidade |
| Complexidade fiscal | Alta | Médio | Baixa | ✅ Validação, sistemas especializados |
| Região específica | Média | Baixo | Baixa | ✅ Validação antes de expandir |
| Infraestrutura internet | Baixa | Médio | Média | ✅ Modo offline (futuro), sincronização |
| Logística regional | Baixa | Baixo | Baixa | ✅ Roteirização flexível |

**Prioridade**: Alta = Mitigar imediatamente, Média = Mitigar quando possível, Baixa = Monitorar

---

## Plano de Mitigação

### Curto Prazo (MVP 1)

1. ✅ Validar assunções do negócio em vendas
2. ✅ Implementar segurança básica (isolamento, HTTPS)
3. ✅ Interface simples e intuitiva
4. ✅ Suporte próximo (primeiras semanas)
5. ✅ Monitoramento básico (logs, erros)

### Médio Prazo (MVP 2-3)

1. ✅ Otimização de performance
2. ✅ **Stock Intelligence Engine**: Garantir que permanece horizontal (não acoplado a vertical)
3. ✅ Escalabilidade (sharding, cache)
4. ✅ Backup automático
5. ✅ Testes automatizados
6. ✅ **Validação de reutilização**: Validar que Stock Intelligence Engine pode ser consumido por outros verticais

### Longo Prazo (MVP 4+)

1. ✅ Alta disponibilidade (99.9%+)
2. ✅ Integração com sistemas externos (validada)
3. ✅ Modo offline completo
4. ✅ Monitoramento avançado
5. ✅ Plano de contingência

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0

