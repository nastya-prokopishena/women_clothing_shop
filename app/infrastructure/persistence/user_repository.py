from bson import ObjectId
from app.extensions import mongo
from app.domain.models.user import User, Address


class UserRepository:
    def __init__(self):
        self.collection = mongo.db.users  # Колекція "users"

    def insert(self, user: User):
        user_dict = user.__dict__.copy()
        user_dict['_id'] = user._id  # ObjectId напряму
        user_dict['surname'] = user.surname
        user_dict['addresses'] = [
            {
                'street': addr.street,
                'city': addr.city,
                'postal_code': addr.postal_code,
                'country': addr.country,
                'house': addr.house,
                '_id': addr._id  # теж ObjectId напряму
            } for addr in user.addresses
        ]

        result = self.collection.insert_one(user_dict)
        user._id = result.inserted_id
        return user

    def find_by_email(self, email: str) -> User:
        data = self.collection.find_one({"email": email})
        if not data:
            return None
        addresses_raw = data.pop('addresses', [])
        addresses = [Address.from_dict(addr) for addr in addresses_raw]
        return User(**data, addresses=addresses)

    def update(self, user: User):
        user_dict = user.__dict__.copy()

        user_dict['addresses'] = [
            {
                'street': addr.street,
                'city': addr.city,
                'postal_code': addr.postal_code,
                'country': addr.country,
                'house': addr.house,
                '_id': addr._id  # ObjectId напряму
            } for addr in user.addresses
        ]

        result = self.collection.update_one(
            {"_id": user._id},  # вже ObjectId
            {"$set": {"addresses": user_dict['addresses'], "phone": user.phone, "password_hash": user.password_hash,
                      "surname": user.surname, "name": user.name,}})

        if result.modified_count == 0:
            print(f"[ERROR] Не оновлено: user_id={user._id}")

    def find_by_id(self, user_id: str) -> User:
        data = self.collection.find_one({"_id": ObjectId(user_id)})
        if not data:
            return None
        addresses = [Address(**addr) for addr in data.get('addresses', [])]
        return User(**data, addresses=addresses)
