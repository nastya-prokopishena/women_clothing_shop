from app.domain.models import Product, ProductAttribute
from app.extensions import mongo
from bson import ObjectId


class ProductRepository:
    def __init__(self):
        self.collection = mongo.db.products

    def _ensure_collection(self):
        """Перевіряє наявність колекції"""
        if self.collection is None:
            raise Exception("Products collection not initialized")

    def find_featured(self, limit=8):
        self._ensure_collection()
        products_data = list(self.collection.find({'is_featured': True}).limit(limit))
        return [self._map_to_product(p) for p in products_data]

    def find_new_arrivals(self, limit=8):
        self._ensure_collection()
        products_data = list(self.collection.find({'is_new': True}).limit(limit))
        return [self._map_to_product(p) for p in products_data]

    def _map_to_product(self, data):
        attributes = ProductAttribute(
            colors=data['attributes']['colors'],
            sizes=data['attributes']['sizes'],
            material=data['attributes'].get('material')
        )
        return Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            categories=data['categories'],
            attributes=attributes,
            images=data['images'],
            stock=data['stock'],
            tags=data['tags'],
            sale_price=data.get('sale_price'),
            rating=data.get('rating', 0.0),
            reviews_count=data.get('reviews_count', 0)
        )
