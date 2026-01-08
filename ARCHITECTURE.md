# Arquitetura do Sistema

## Visão Geral

Sistema multi-tenant SaaS para gestão de cotações e pedidos em lojas de materiais de construção.

## Diagrama Lógico

```
┌─────────────────┐
│   Frontend      │  React (Desktop-first)
│   (React)       │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend API   │  FastAPI
│   (FastAPI)     │
└────────┬────────┘
         │
         │ SQL
         │
┌────────▼────────┐
│   PostgreSQL    │  Multi-tenant por tenant_id
│   (Database)    │
└─────────────────┘
```

## Principais Entidades

### Tenant (Loja)
- Representa uma loja de materiais de construção
- Cada tenant tem isolamento completo de dados

### Cliente
- PF (Pessoa Física) ou PJ (Pessoa Jurídica)
- Vinculado a um tenant
- Pode ter múltiplas obras

### Obra (Opcional)
- Vinculada a um cliente
- Permite preços diferenciados por obra

### Produto
- Catálogo de produtos da loja
- Preço base por produto
- Vinculado ao tenant

### Cotação
- Lista de produtos com quantidades
- Regras de preço aplicadas
- Status: rascunho → enviada → aprovada → convertida
- Histórico versionado

### Pedido
- Convertido de uma cotação
- Representa um pedido confirmado
- Status de entrega básico

## Fluxo de Dados

1. **Criação de Cotação**
   - Seleciona cliente (e opcionalmente obra)
   - Adiciona produtos com quantidades
   - Aplica regras de preço (desconto)
   - Salva como rascunho

2. **Envio de Cotação**
   - Marca status como "enviada"
   - Cliente visualiza (futuro)

3. **Aprovação**
   - Cliente aprova (manual ou futuro sistema)

4. **Conversão em Pedido**
   - Um clique converte cotação aprovada em pedido
   - Pedido herda todos os itens da cotação

## Multi-tenant

**Estratégia**: Tenant ID em todas as tabelas + Middleware

- Todas as queries são filtradas por `tenant_id`
- Middleware extrai `tenant_id` do token JWT
- Isolamento garantido no nível da aplicação

## Segurança

- JWT para autenticação
- Tenant isolation obrigatório
- Validação de dados em todas as entradas
- CORS configurado para produção

