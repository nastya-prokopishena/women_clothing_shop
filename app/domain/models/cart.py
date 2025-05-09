from datetime import datetime
from typing import List, Optional


class CartItem:
    def __init__(self, product_id: str, quantity: int, size: str, color: str):
        self.product_id = product_id
        self.quantity = quantity
        self.size = size
        self.color = color
        self.added_at = datetime.utcnow()


class Cart:
    def __init__(self, user_id: Optional[str] = None, session_id: Optional[str] = None,
                 items: Optional[List[CartItem]] = None, coupon_code: Optional[str] = None,
                 discount_amount: float = 0.0):
        self.user_id = user_id
        self.session_id = session_id
        self.items = items or []
        self.coupon_code = coupon_code
        self.discount_amount = discount_amount
        self.last_updated = datetime.utcnow()