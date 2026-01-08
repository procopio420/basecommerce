"""
Stock Intelligence Engine

Engine horizontal que ajuda a decidir O QUE comprar, QUANDO comprar e QUANTO comprar.
Fornece alertas de risco de ruptura, sugestões de reposição e análise ABC.
"""

from app.core_engines.stock_intelligence.implementation import StockIntelligenceImplementation
from app.core_engines.stock_intelligence.ports import StockIntelligencePort
from app.core_engines.stock_intelligence.stub import StockIntelligenceStub

__all__ = [
    "StockIntelligencePort",
    "StockIntelligenceStub",
    "StockIntelligenceImplementation",
]
