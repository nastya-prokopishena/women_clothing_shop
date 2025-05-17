import pytest
from app import create_app
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_women_clothing_shop'
    app.config['SERVER_NAME'] = 'localhost'  # Додаємо SERVER_NAME
    app.config['APPLICATION_ROOT'] = '/'  # Додаємо APPLICATION_ROOT
    app.config['PREFERRED_URL_SCHEME'] = 'http'  # Додаємо PREFERRED_URL_SCHEME

    with app.app_context():
        mongo.init_app(app)
        # Очищаємо базу даних перед тестами
        for collection in mongo.db.list_collection_names():
            mongo.db.drop_collection(collection)

        # Додаємо тестові дані
        add_test_data(mongo.db)

        yield app

        # Очищаємо базу даних після тестів
        for collection in mongo.db.list_collection_names():
            mongo.db.drop_collection(collection)


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


def add_test_data(db):
    # Додаємо тестові категорії
    categories = [
        {
            "_id": ObjectId("5f8d8f7d8f7d8f7d8f7d8f71"),
            "name": "Dresses",
            "slug": "dresses",
            "is_featured": True
        },
        {
            "_id": ObjectId("5f8d8f7d8f7d8f7d8f7d8f72"),
            "name": "Tops",
            "slug": "tops",
            "is_featured": False
        }
    ]
    db.categories.insert_many(categories)

    # Додаємо тестові продукти
    products = [
        {
            "_id": ObjectId("5f8d8f7d8f7d8f7d8f7d8f81"),
            "name": "Floral Dress",
            "price": 899,
            "category_slug": "dresses",
            "images": ["dress1.jpg"],
            "attributes": {
                "colors": ["red", "blue"],
                "sizes": ["S", "M", "L"]
            },
            "is_new": True,
            "stock": 10
        },
        {
            "_id": ObjectId("5f8d8f7d8f7d8f7d8f7d8f82"),
            "name": "Summer Top",
            "price": 499,
            "category_slug": "tops",
            "images": ["top1.jpg"],
            "attributes": {
                "colors": ["white"],
                "sizes": ["S", "M"]
            },
            "is_new": False,
            "stock": 5
        }
    ]
    db.products.insert_many(products)

    # Додаємо тестові відгуки
    reviews = [
        {
            "product_id": "5f8d8f7d8f7d8f7d8f7d8f81",
            "user_name": "Anna",
            "text": "Beautiful dress!",
            "rating": 5,
            "created_at": datetime.now()
        },
        {
            "product_id": "5f8d8f7d8f7d8f7d8f7d8f81",
            "user_name": "Maria",
            "text": "Fits perfectly",
            "rating": 4,
            "created_at": datetime.now()
        }
    ]
    db.reviews.insert_many(reviews)