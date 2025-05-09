from datetime import datetime
from typing import List, Optional


class ProductAttribute:
    def __init__(self, colors: List[str], sizes: List[str], material: Optional[str] = None):
        self.colors = colors
        self.sizes = sizes
        self.material = material


class Product:
    def __init__(self, name: str, description: str, price: float, categories: List[str],
                 attributes: ProductAttribute, images: List[str], stock: int, tags: List[str],
                 sale_price: Optional[float] = None):
        self.name = name
        self.description = description
        self.price = price
        self.categories = categories
        self.attributes = attributes
        self.images = images
        self.stock = stock
        self.tags = tags
        self.sale_price = sale_price
        self.rating = 0.0
        self.reviews_count = 0
        self.created_at = datetime.utcnow()