from app.domain.models import Review
from app.extensions import mongo
from bson import ObjectId

class ReviewRepository:
    def __init__(self):
        self.collection = mongo.db.reviews

    def find_for_homepage(self, limit=5):
        reviews_data = list(self.collection.aggregate([
            {'$sort': {'created_at': -1}},
            {'$limit': limit},
            {'$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }},
            {'$unwind': '$user'},
            {'$project': {
                'user_name': '$user.name',
                'rating': 1,
                'text': 1,
                'created_at': 1
            }}
        ]))
        return [self._map_to_review(r) for r in reviews_data]

    def _map_to_review(self, data):
        return Review(
            id=str(data['_id']),
            product_id=str(data.get('product_id', '')),
            user_id=str(data.get('user_id', '')),
            user_name=data['user_name'],
            rating=data['rating'],
            text=data['text'],
            images=data.get('images', [])
        )