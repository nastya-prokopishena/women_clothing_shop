from app.domain.models.user import User, Address
from bson import ObjectId
import hashlib


class UserService:
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.hash_password(plain_password) == hashed_password

    def create_user(self, name: str, email: str, password_hash: str):
        return User(name=name, email=email, password_hash=password_hash)

    def create_address(self, street: str, city: str, postal_code: str, country: str, house: str = ""):
        address = Address(street, city, postal_code, country, house)
        address._id = str(ObjectId())
        return address
