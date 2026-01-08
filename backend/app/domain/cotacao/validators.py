"""
Validadores de domínio para cotações
"""

from decimal import Decimal

from app.domain.cotacao.exceptions import (
    CotacaoNaoPodeSerEnviadaException,
)


def validar_cotacao_para_envio(itens: list, desconto_percentual: Decimal) -> None:
    """
    Valida se cotação pode ser enviada.

    Regras:
    - Deve ter pelo menos 1 item
    - Desconto percentual não pode ser negativo ou maior que 100
    """
    if not itens or len(itens) == 0:
        raise CotacaoNaoPodeSerEnviadaException(
            "Cotação deve ter pelo menos um item para ser enviada"
        )

    if desconto_percentual < 0 or desconto_percentual > 100:
        raise CotacaoNaoPodeSerEnviadaException("Desconto percentual deve estar entre 0 e 100")


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
