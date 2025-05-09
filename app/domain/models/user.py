from datetime import datetime
from typing import List, Optional


class Address:
    def __init__(self, street: str, city: str, postal_code: str, country: str, is_default: bool = False):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.is_default = is_default


class User:
    def __init__(self, name: str, email: str, password_hash: str, phone: Optional[str] = None,
                 addresses: Optional[List[Address]] = None, favorites: Optional[List[str]] = None,
                 newsletter_sub: bool = False):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.addresses = addresses or []
        self.favorites = favorites or []
        self.newsletter_sub = newsletter_sub
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()