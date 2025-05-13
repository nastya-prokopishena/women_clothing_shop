from app.domain.models import Category
from app.extensions import mongo
from bson import ObjectId


class CategoryRepository:
    def __init__(self):
        self.collection = mongo.db.categories

    def find_featured(self, limit=6):
        categories_data = list(self.collection.find({'is_featured': True}).limit(limit))
        return [self._map_to_category(c) for c in categories_data]

    def _map_to_category(self, data):
        return Category(
            name=data['name'],
            slug=data['slug'],
            parent_id=str(data['parent_id']) if data.get('parent_id') else None,
            image=data.get('image'),
            is_featured=data.get('is_featured', False)
        )
