from datetime import datetime
from typing import List, Optional
from bson import ObjectId


class Address:
    def __init__(self, street: str, city: str, postal_code: str, country: str, house: str, is_default: bool = False,
                 _id=None):
        self.house = house
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        # self.is_default = is_default
        self._id = _id if _id else ObjectId()

    @classmethod
    def from_dict(cls, data: dict):
        _id = data.get("_id")
        if _id and not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        return cls(street=data.get("street", ""), city=data.get("city", ""), postal_code=data.get("postal_code", ""),
                   country=data.get("country", ""), house=data.get("house", ""), _id=_id)


class User:
    def __init__(self, name: str, email: str, password_hash: str, phone: Optional[str] = None,
                 surname: Optional[str] = None, addresses: Optional[List[Address]] = None,
                 favorites: Optional[List[str]] = None, newsletter_sub: bool = False, reset_token: Optional[str] = None,
                 reset_token_created_at: Optional[datetime] = None, _id=None):
        self.name = name
        self.surname = surname
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.addresses = addresses or []
        # self.favorites = favorites or []
        # self.newsletter_sub = newsletter_sub
        # self.created_at = datetime.utcnow()
        # self.updated_at = datetime.utcnow()
        self._id = _id if _id else ObjectId()
        self.reset_token = reset_token
        self.reset_token_created_at = reset_token_created_at
