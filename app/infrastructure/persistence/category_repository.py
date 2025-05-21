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

    def find_featured(self, limit=None):
        query = {'is_featured': True}
        categories_data = list(
            self.collection.find(query) if limit is None else self.collection.find(query).limit(limit))
        return [self._map_to_category(c) for c in categories_data]

    def find_all_with_counts(self):
        pipeline = [
            {
                '$lookup': {
                    'from': 'products',
                    'localField': 'slug',
                    'foreignField': 'category_slug',
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
        print([c['name'] for c in categories_data])
        return [self._map_to_category(c) for c in categories_data]

    def _map_to_category(self, data):
        return Category(
            id=str(data['_id']),
            name=data['name'],
            slug=data['slug'],
            is_featured=data.get('is_featured', False),
            products_count=data.get('products_count', 0)
        )