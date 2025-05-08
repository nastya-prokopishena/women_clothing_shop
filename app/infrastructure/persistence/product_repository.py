from typing import Optional, List
from app.domain.models.product import Product
import json


class ProductRepository:
    def __init__(self, data_file: str = "products.json"):
        self.data_file = data_file
        self.products = self._load_products()

    def _load_products(self) -> List[Product]:
        """Завантаження продуктів з JSON файлу"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                return [Product(**item) for item in data]
        except FileNotFoundError:
            return []

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Знайти продукт по ID"""
        return next((p for p in self.products if p.id == product_id), None)

    def get_related_products(self, category: str, exclude_id: str) -> List[Product]:
        """Отримати схожі продукти"""
        return [p for p in self.products
                if p.category == category
                and p.id != exclude_id][:4]
