import pytest
from app.domain.models.user import User
from app.infrastructure.persistence.user_repository import UserRepository
from bson import ObjectId
from datetime import datetime

# Тестовий користувач
TEST_USER_ID = "681cf5dceb18aa5a6197c3d1"
TEST_EMAIL = "dari1@gmail.com"
TEST_NAME = "dari"
TEST_PASSWORD = "1234"


@pytest.fixture
def setup_user(app):
    # Додаємо тестового користувача перед тестами
    with app.app_context():
        user_data = {
            "_id": TEST_USER_ID,
            "name": TEST_NAME,
            "email": TEST_EMAIL,
            "password_hash": TEST_PASSWORD,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        mongo.db.users.insert_one(user_data)
        yield
        # Очищаємо після тестів
        mongo.db.users.delete_many({})


def test_get_by_id(app, setup_user):
    with app.app_context():
        user = UserRepository.get_by_id(TEST_USER_ID)
        assert user is not None
        assert user._id == TEST_USER_ID
        assert user.email == TEST_EMAIL
        assert user.name == TEST_NAME


def test_get_by_email(app, setup_user):
    with app.app_context():
        user = UserRepository.get_by_email(TEST_EMAIL)
        assert user is not None
        assert user.email == TEST_EMAIL
        assert user.name == TEST_NAME


def test_update_user(app, setup_user):
    with app.app_context():
        new_name = "Daria Updated"
        updated_user = UserRepository.update(TEST_USER_ID, {"name": new_name})
        assert updated_user is not None
        assert updated_user.name == new_name


def test_create_and_delete_user(app):
    with app.app_context():
        test_email = "test_new_user@example.com"
        new_user = User(
            _id="test_id_123",  # Додаємо _id
            name="Test User",
            email=test_email,
            password_hash="test_hash",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        created_user = UserRepository.create(new_user)
        assert created_user._id is not None

        # Тестуємо видалення (додайте метод delete у UserRepository)
        # UserRepository.delete(created_user._id)
        # assert UserRepository.get_by_id(created_user._id) is None