from app.domain.models import Product, ProductAttribute
from app.infrastructure.persistence.product_repository import ProductRepository
from typing import Optional


class ProductPageService:
    def __init__(self):
        self.repository = ProductRepository()

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Отримати продукт за ID"""
        return self.repository.get_product_by_id(product_id)

    def get_related_products(self, product: Product, limit: int = 4) -> list[Product]:
        """Отримати схожі товари"""
        return self.repository.get_related_products(
            categories=product.categories,
            exclude_id=product.product_id,
            limit=limit
        )