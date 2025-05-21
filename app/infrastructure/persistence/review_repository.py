from app.domain.models import Review
from app.extensions import mongo
from datetime import datetime
from random import sample, random


class ReviewRepository:
    def __init__(self):
        self.collection = mongo.db.reviews

    # Додано метод для збереження нового коментаря
    def add_review(self, product_id: str, text: str, author: str, rating: int):
        review_data = {
            "product_id": product_id,
            "text": text,
            "author": author,
            "created_at": datetime.now(),
            "rating": rating,
            # Якщо потрібно додати user_id для авторизованих користувачів:
            # "user_id": user_id,
        }
        result = self.collection.insert_one(review_data)
        return str(result.inserted_id)

    # Оновлений метод для отримання коментарів товару
    def get_reviews_by_product_id(self, product_id: str):
        reviews_data = self.collection.find({"product_id": product_id}).sort("created_at", -1)
        return [self._map_to_review(r) for r in reviews_data]

    # Метод для головної сторінки (залишається без змін)
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

    # Оновлений маппінг з урахуванням нових полів
    def _map_to_review(self, data):
        return Review(
            id=str(data['_id']),
            product_id=str(data['product_id']),
            user_name=data.get('author', 'Гість'),
            text=data['text'],
            created_at=data['created_at'],
            rating=data.get('rating', 0),
            images=data.get('images', [])
        )

    def get_random_reviews(self, limit=10):
        all_reviews = list(self.collection.find())

        if len(all_reviews) <= limit:
            reviews_data = all_reviews
        else:
            reviews_data = sample(all_reviews, limit)

        return [self._map_to_review(r) for r in reviews_data]