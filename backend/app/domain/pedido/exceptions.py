"""
Exceções do domínio de pedidos
"""


class PedidoDomainError(Exception):
    """Exceção base do domínio de pedidos"""

    pass


# Alias para compatibilidade
PedidoDomainException = PedidoDomainError


class PedidoNaoPodeSerEditadoException(PedidoDomainException):
    """Exceção lançada quando tentativa de editar pedido já criado"""

    pass


class PedidoNaoPodeSerCanceladoException(PedidoDomainException):
    """Exceção lançada quando tentativa de cancelar pedido que não pode ser cancelado"""

    pass


class ConversaoCotacaoException(PedidoDomainException):
    """Exceção base para erros na conversão de cotação em pedido"""

    pass


class CotacaoNaoAprovadaException(ConversaoCotacaoException):
    """Exceção lançada quando tentativa de converter cotação não aprovada"""

    pass


class CotacaoJaConvertidaException(ConversaoCotacaoException):
    """Exceção lançada quando tentativa de converter cotação já convertida"""

    pass


class CotacaoSemItensException(ConversaoCotacaoException):
    """Exceção lançada quando tentativa de converter cotação sem itens"""

    pass
