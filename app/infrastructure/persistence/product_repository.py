from app.domain.models import Product, ProductAttribute
from app.extensions import mongo
from bson import ObjectId
from typing import Optional, List


class ProductRepository:
    def __init__(self):
        self.collection = mongo.db.products

    def _ensure_collection(self):
        """Перевіряє наявність колекції"""
        if self.collection is None:
            raise Exception("Products collection not initialized")

    def find_featured(self, limit=8):
        products_data = list(self.collection.find({'is_featured': True}).limit(limit))
        return [self._map_to_product(p) for p in products_data]

    def find_all(self):
        self._ensure_collection()
        products_data = list(self.collection.find())
        return [self._map_to_product(p) for p in products_data]

    def find_new_arrivals(self, limit=8):
        self._ensure_collection()
        products_data = list(self.collection.find({'is_new': True}).limit(limit))
        return [self._map_to_product(p) for p in products_data]

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Отримати продукт за ID"""
        self._ensure_collection()
        try:
            data = self.collection.find_one({'_id': ObjectId(product_id)})
        except Exception:
            return None
        if data:
            return self._map_to_product(data)
        return None

    def find_by_category(self, category_slug: str) -> List[Product]:
        self._ensure_collection()
        products_data = list(self.collection.find({'category_slug': category_slug}))
        return [self._map_to_product(p) for p in products_data]

    def get_related_products(self, category_slug: str, exclude_id: str, limit: int = 4) -> List[Product]:
        self._ensure_collection()
        products_data = self.collection.find({
            'category_slug': category_slug,
            '_id': {'$ne': ObjectId(exclude_id)}
        }).limit(limit)
        return [self._map_to_product(p) for p in products_data]

    def _map_to_product(self, data):
        attributes = ProductAttribute(
            colors=data['attributes']['colors'],
            sizes=data['attributes']['sizes'],
            material=data['attributes'].get('material')
        )
        return Product(
            name=data['name'],
            care=data['care'],
            description=data['description'],
            price=data['price'],
            category_id=data.get('category_slug'),
            attributes=attributes,
            images=data['images'],
            stock=data['stock'],
            product_id=str(data['_id'])
        )
