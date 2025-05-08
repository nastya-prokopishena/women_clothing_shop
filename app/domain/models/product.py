from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    id: str
    name: str
    description: str
    price: Decimal
    sizes: list[str]
    colors: list[str]
    images: list[str]
    category: str
    sku: str
