import pytest
from app import create_app
from app.extensions import mongo


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_women_clothing_shop'

    with app.app_context():
        mongo.init_app(app)
        yield app


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()