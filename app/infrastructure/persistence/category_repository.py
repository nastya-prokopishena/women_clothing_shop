# app/infrastructure/persistence/category_repository.py
from app.domain.models import Category
from app.extensions import mongo
from bson import ObjectId


class CategoryRepository:
    def __init__(self):
        self.collection = mongo.db.categories

    def find_all(self):
        categories_data = list(self.collection.find())
        return [self._map_to_category(c) for c in categories_data]

    def find_by_slug(self, slug: str):
        category_data = self.collection.find_one({'slug': slug})
        if not category_data:
            return None
        return self._map_to_category(category_data)

    def find_featured(self, limit=6):
        categories_data = list(self.collection.find({'is_featured': True}).limit(limit))
        return [self._map_to_category(c) for c in categories_data]

    def find_all_with_counts(self):
        pipeline = [
            {
                '$lookup': {
                    'from': 'products',
                    'localField': '_id',
                    'foreignField': 'category_id',
                    'as': 'products'
                }
            },
            {
                '$addFields': {
                    'products_count': {'$size': '$products'}
                }
            }
        ]
        categories_data = list(self.collection.aggregate(pipeline))
        return [self._map_to_category(c) for c in categories_data]

    def _map_to_category(self, data):
        return Category(
            id=str(data['_id']),
            name=data['name'],
            slug=data['slug'],
            is_featured=data.get('is_featured', False)
        )