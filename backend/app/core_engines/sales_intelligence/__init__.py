"""
Sales Intelligence Engine

Engine horizontal que ajuda a AUMENTAR o valor da venda com sugestões lógicas.
Fornece sugestões de produtos complementares, substitutos e bundles.
"""

from app.core_engines.sales_intelligence.implementation import SalesIntelligenceImplementation
from app.core_engines.sales_intelligence.ports import SalesIntelligencePort
from app.core_engines.sales_intelligence.stub import SalesIntelligenceStub

__all__ = [
    "SalesIntelligencePort",
    "SalesIntelligenceStub",
    "SalesIntelligenceImplementation",
]
