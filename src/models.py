"""
Veri modelleri
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ProductImage:
    url: str
    is_main: bool = False


@dataclass
class ProductVariation:
    color: str
    size: str
    sku: str
    stock: int
    regular_price: float
    sale_price: float = 0.0


@dataclass
class Product:
    name: str
    category: str
    description: str
    short_description: str
    sku: str

    images: List[ProductImage] = field(default_factory=list)

    variations: List[ProductVariation] = field(default_factory=list)
