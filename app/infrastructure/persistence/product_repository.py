from typing import Optional, List
from app.domain.models.product import Product
from app.extensions import mongo  # Імпортуємо mongo екземпляр
from decimal import Decimal


class ProductRepository:
    def __init__(self):
        self.collection = mongo.db.products  # Назва колекції

    def _document_to_product(self, doc: dict) -> Product:
        """Конвертує документ з MongoDB у Product"""
        return Product(
            id=str(doc['_id']),
            name=doc['name'],
            description=doc.get('description', ''),
            price=Decimal(str(doc['price'])),
            sizes=doc.get('sizes', []),
            colors=doc.get('colors', []),
            images=doc.get('images', []),
            category=doc['category'],
            sku=doc['sku']
        )

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Знайти продукт по ID"""
        doc = self.collection.find_one({'_id': product_id})
        if doc:
            return self._document_to_product(doc)
        return None

    def get_related_products(self, category: str, exclude_id: str) -> List[Product]:
        """Отримати схожі продукти"""
        docs = self.collection.find({
            'category': category,
            '_id': {'$ne': exclude_id}
        }).limit(4)

        return [self._document_to_product(doc) for doc in docs]
