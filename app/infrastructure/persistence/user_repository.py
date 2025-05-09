from bson import ObjectId
from app.extensions import mongo
from app.domain.models.user import User, Address


class UserRepository:
    def __init__(self):
        self.collection = mongo.db.users  # Колекція "users"

    def insert(self, user: User):
        user_dict = user.__dict__.copy()
        user_dict['addresses'] = [addr.__dict__ for addr in user.addresses]
        result = self.collection.insert_one(user_dict)
        user._id = result.inserted_id
        return user

    def find_by_email(self, email: str) -> User:
        data = self.collection.find_one({"email": email})
        if not data:
            return None
        addresses = [Address(**addr) for addr in data.get('addresses', [])]
        return User(**data, addresses=addresses)

    def update(self, user: User):
        user_dict = user.__dict__.copy()
        user_dict['addresses'] = [addr.__dict__ for addr in user.addresses]
        self.collection.update_one({"_id": ObjectId(user._id)}, {"$set": user_dict})

    def find_by_id(self, user_id: str) -> User:
        data = self.collection.find_one({"_id": ObjectId(user_id)})
        if not data:
            return None
        addresses = [Address(**addr) for addr in data.get('addresses', [])]
        return User(**data, addresses=addresses)
