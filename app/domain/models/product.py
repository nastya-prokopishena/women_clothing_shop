from typing import List, Optional


class ProductAttribute:
    def __init__(self, colors: List[str], sizes: List[str], material: Optional[str] = None):
        self.colors = colors
        self.sizes = sizes
        self.material = material


class Product:
    def __init__(self, name: str, care: str, description: str, price: float, category_id: str,
                 attributes: ProductAttribute, images: List[str], stock: int,
                 product_id: Optional[str] = None):
        self.product_id = product_id  # зберігаємо його
        self.name = name
        self.care = care
        self.description = description
        self.price = price
        self.category_slug = category_id
        self.attributes = attributes
        self.images = images
        self.stock = stock
        self.rating = 0.0
        self.reviews_count = 0
