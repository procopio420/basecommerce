"""
Validadores de domínio para pedidos
"""

from decimal import Decimal


def calcular_valor_total_item(
    quantidade: Decimal, preco_unitario: Decimal, desconto_percentual: Decimal
) -> Decimal:
    """
    Calcula valor total de um item aplicando desconto.

    Fórmula: (quantidade × preco_unitario) × (1 - desconto_percentual / 100)
    """
    subtotal = quantidade * preco_unitario
    desconto_valor = subtotal * (desconto_percentual / Decimal("100"))
    return subtotal - desconto_valor
