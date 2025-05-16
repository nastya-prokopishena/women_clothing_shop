from flask import Flask
from app.config import Config
from app.extensions import mongo
from app.web.routes.auth import bp as auth_bp
import os
from app.extensions import mail
from urllib.parse import quote_plus
from pymongo.errors import ConnectionFailure, OperationFailure
import sys


def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMPLATE_DIR = os.path.join(BASE_DIR, 'web', 'templates')
    STATIC_DIR = os.path.join(BASE_DIR, 'web', 'static')

    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
    app.config.from_object(Config)

    app.secret_key = 'your-secret-key'

    # Підключаємо Blueprint для auth
    app.register_blueprint(auth_bp)

    print("\n=== Initializing MongoDB Connection ===")
    print(f"Using MONGO_URI: {app.config['MONGO_URI']}")

    try:
        mail.init_app(app)  # для токену для скидання паролю
        print("✅ Flask-Mail initialized")

        # Ініціалізація MongoDB
        mongo.init_app(app, uri=app.config['MONGO_URI'])

        with app.app_context():
            try:
                print("Attempting to ping MongoDB...")
                mongo.cx.admin.command('ping')
                print("✅ MongoDB connection successful!")

                # Отримуємо об'єкт конкретної бази даних
                db_name = app.config['MONGO_URI'].split('/')[-1].split('?')[0]
                db = mongo.cx[db_name]  # Використовуємо cx замість db

                print(f"Using database: {db_name}")

                # Перевірка наявності колекцій
                required_collections = ['users', 'products', 'categories',
                                        'reviews', 'orders', 'carts', 'coupons']

                print("\n=== Checking Collections ===")
                existing_collections = db.list_collection_names()

                for collection in required_collections:
                    if collection not in existing_collections:
                        db.create_collection(collection)
                        print(f"🆕 Created collection: {collection}")
                    else:
                        print(f"✔️ Collection exists: {collection}")

                # Створення індексів
                print("\n=== Creating Indexes ===")
                create_indexes(db)

            except Exception as e:
                print(f"❌ Database operation error: {e}")
                raise

    except Exception as e:
        print(f"❌ Failed to initialize MongoDB: {e}")
        raise

    # Підключення маршрутів
    from app.web.routes.main import init_main_routes
    init_main_routes(app)

    print("\n=== Application initialized successfully ===")
    return app


def create_indexes(db):
    """Створення необхідних індексів"""
    try:
        # Users
        db.users.create_index("email", unique=True)

        # Products
        db.products.create_index([("name", "text"), ("description", "text")])
        db.products.create_index("is_featured")
        db.products.create_index("is_new")

        # Categories
        db.categories.create_index("slug", unique=True)

        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️ Error creating indexes: {e}")