"""
Pricing & Supplier Intelligence Engine

Engine horizontal que ajuda a decidir DE QUEM comprar e A QUE CUSTO.
Fornece comparação de fornecedores, custo base e alertas de variação de preço.
"""

from app.core_engines.pricing_supplier.implementation import (
    PricingSupplierIntelligenceImplementation,
)
from app.core_engines.pricing_supplier.ports import PricingSupplierIntelligencePort
from app.core_engines.pricing_supplier.stub import PricingSupplierIntelligenceStub

__all__ = [
    "PricingSupplierIntelligencePort",
    "PricingSupplierIntelligenceStub",
    "PricingSupplierIntelligenceImplementation",
]
