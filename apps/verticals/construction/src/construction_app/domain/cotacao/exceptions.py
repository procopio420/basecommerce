"""
Exceções do domínio de cotações
"""


class CotacaoDomainError(Exception):
    """Exceção base do domínio de cotações"""

    pass


# Alias para compatibilidade
CotacaoDomainException = CotacaoDomainError


class CotacaoNaoPodeSerEditadaException(CotacaoDomainException):
    """Exceção lançada quando tentativa de editar cotação que não está em rascunho"""

    pass


class CotacaoNaoPodeSerEnviadaException(CotacaoDomainException):
    """Exceção lançada quando tentativa de enviar cotação inválida"""

    pass


class CotacaoNaoPodeSerAprovadaException(CotacaoDomainException):
    """Exceção lançada quando tentativa de aprovar cotação que não está enviada"""

    pass


class CotacaoNaoPodeSerConvertidaException(CotacaoDomainException):
    """Exceção lançada quando tentativa de converter cotação que não está aprovada"""

    pass


class CotacaoJaConvertidaException(CotacaoDomainException):
    """Exceção lançada quando tentativa de converter cotação já convertida"""

    pass
