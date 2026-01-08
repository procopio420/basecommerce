"""
Testes básicos de fluxo de cotações

Testa o fluxo completo: criar cotação → enviar → aprovar → converter em pedido
"""

import pytest
from fastapi import status


def test_criar_cotacao(client, auth_headers, cliente, produto):
    """Testa criação de cotação básica"""
    cotacao_data = {
        "cliente_id": str(cliente.id),
        "desconto_percentual": "0",
        "observacoes": "Teste de cotação",
        "validade_dias": 7,
        "itens": [
            {
                "produto_id": str(produto.id),
                "quantidade": "10",
                "preco_unitario": "32.00",
                "desconto_percentual": "0",
                "observacoes": None,
                "ordem": 0,
            }
        ],
    }

    response = client.post("/api/v1/cotacoes/", json=cotacao_data, headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["status"] == "rascunho"
    assert data["numero"].startswith("COT-")
    assert len(data["itens"]) == 1
    assert data["itens"][0]["quantidade"] == "10.000"
    assert data["itens"][0]["preco_unitario"] == "32.00"
    assert data["itens"][0]["valor_total"] == "320.00"

    return data


def test_enviar_cotacao(client, auth_headers, cliente, produto):
    """Testa envio de cotação"""
    # Cria cotação primeiro
    cotacao_data = {
        "cliente_id": str(cliente.id),
        "desconto_percentual": "0",
        "validade_dias": 7,
        "itens": [
            {
                "produto_id": str(produto.id),
                "quantidade": "10",
                "preco_unitario": "32.00",
                "desconto_percentual": "0",
                "ordem": 0,
            }
        ],
    }

    response = client.post("/api/v1/cotacoes/", json=cotacao_data, headers=auth_headers)
    cotacao_id = response.json()["id"]

    # Envia cotação
    response = client.post(f"/api/v1/cotacoes/{cotacao_id}/enviar", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "enviada"
    assert data["enviada_em"] is not None


def test_aprovar_cotacao(client, auth_headers, cliente, produto):
    """Testa aprovação de cotação"""
    # Cria e envia cotação
    cotacao_data = {
        "cliente_id": str(cliente.id),
        "desconto_percentual": "0",
        "validade_dias": 7,
        "itens": [
            {
                "produto_id": str(produto.id),
                "quantidade": "10",
                "preco_unitario": "32.00",
                "desconto_percentual": "0",
                "ordem": 0,
            }
        ],
    }

    response = client.post("/api/v1/cotacoes/", json=cotacao_data, headers=auth_headers)
    cotacao_id = response.json()["id"]

    response = client.post(f"/api/v1/cotacoes/{cotacao_id}/enviar", headers=auth_headers)

    # Aprova cotação
    response = client.post(f"/api/v1/cotacoes/{cotacao_id}/aprovar", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "aprovada"
    assert data["aprovada_em"] is not None

    return cotacao_id


def test_converter_cotacao_em_pedido(client, auth_headers, cliente, produto):
    """
    Testa conversão de cotação aprovada em pedido (fluxo principal do MVP 1).

    Este é o teste mais importante do MVP 1.
    """
    # Cria, envia e aprova cotação
    cotacao_id = test_aprovar_cotacao(client, auth_headers, cliente, produto)

    # Converte em pedido
    response = client.post(f"/api/v1/pedidos/from-cotacao/{cotacao_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Verifica que pedido foi criado
    assert data["numero"].startswith("PED-")
    assert data["status"] == "pendente"
    assert data["cotacao_id"] == cotacao_id
    assert data["cliente_id"] == str(cliente.id)
    assert len(data["itens"]) == 1

    # Verifica que itens foram copiados corretamente (preços "congelados")
    pedido_item = data["itens"][0]
    assert pedido_item["quantidade"] == "10.000"
    assert pedido_item["preco_unitario"] == "32.00"
    assert pedido_item["valor_total"] == "320.00"

    # Verifica que cotação foi marcada como convertida
    response = client.get(f"/api/v1/cotacoes/{cotacao_id}", headers=auth_headers)
    cotacao = response.json()
    assert cotacao["status"] == "convertida"
    assert cotacao["convertida_em"] is not None


def test_nao_pode_converter_cotacao_nao_aprovada(client, auth_headers, cliente, produto):
    """Testa que não pode converter cotação que não está aprovada"""
    # Cria cotação (em rascunho)
    cotacao_data = {
        "cliente_id": str(cliente.id),
        "desconto_percentual": "0",
        "validade_dias": 7,
        "itens": [
            {
                "produto_id": str(produto.id),
                "quantidade": "10",
                "preco_unitario": "32.00",
                "desconto_percentual": "0",
                "ordem": 0,
            }
        ],
    }

    response = client.post("/api/v1/cotacoes/", json=cotacao_data, headers=auth_headers)
    cotacao_id = response.json()["id"]

    # Tenta converter (deve falhar)
    response = client.post(f"/api/v1/pedidos/from-cotacao/{cotacao_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "aprovadas" in response.json()["detail"].lower()


def test_converter_cotacao_ja_convertida_retorna_pedido_existente(
    client, auth_headers, cliente, produto
):
    """Testa que converter cotação já convertida retorna o pedido existente (idempotência)"""
    # Cria, aprova e converte cotação
    cotacao_id = test_aprovar_cotacao(client, auth_headers, cliente, produto)

    response = client.post(f"/api/v1/pedidos/from-cotacao/{cotacao_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    primeiro_pedido = response.json()
    primeiro_pedido_id = primeiro_pedido["id"]

    # Tenta converter novamente (deve retornar o mesmo pedido - idempotência)
    response = client.post(f"/api/v1/pedidos/from-cotacao/{cotacao_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    segundo_pedido = response.json()

    # Verifica que retornou o mesmo pedido (idempotência)
    assert segundo_pedido["id"] == primeiro_pedido_id
    assert segundo_pedido["numero"] == primeiro_pedido["numero"]


def test_nao_pode_editar_cotacao_enviada(client, auth_headers, cliente, produto):
    """Testa que não pode editar cotação que já foi enviada"""
    # Cria e envia cotação
    cotacao_data = {
        "cliente_id": str(cliente.id),
        "desconto_percentual": "0",
        "validade_dias": 7,
        "itens": [
            {
                "produto_id": str(produto.id),
                "quantidade": "10",
                "preco_unitario": "32.00",
                "desconto_percentual": "0",
                "ordem": 0,
            }
        ],
    }

    response = client.post("/api/v1/cotacoes/", json=cotacao_data, headers=auth_headers)
    cotacao_id = response.json()["id"]

    response = client.post(f"/api/v1/cotacoes/{cotacao_id}/enviar", headers=auth_headers)

    # Tenta editar (deve falhar)
    update_data = {"observacoes": "Nova observação"}

    response = client.put(f"/api/v1/cotacoes/{cotacao_id}", json=update_data, headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "rascunho" in response.json()["detail"].lower()
