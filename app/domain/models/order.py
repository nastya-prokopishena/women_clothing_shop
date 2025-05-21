from datetime import datetime
from typing import List, Optional


class OrderItem:
    def __init__(self, product_id: str, quantity: int, price: float, size: str, color: str):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.size = size
        self.color = color


class Order:
    def __init__(self, user_id: str, items: List[OrderItem], total_amount: float, shipping_address: dict,
                 payment_method: str, delivery_method: str, delivery_cost: float, status: str = "processing",
                 tracking_number: Optional[str] = None, notes: Optional[str] = None):
        self.user_id = user_id
        self.items = items
        self.total_amount = total_amount
        self.shipping_address = shipping_address
        self.payment_method = payment_method
        self.payment_status = "pending"
        self.delivery_method = delivery_method
        self.delivery_cost = delivery_cost
        self.status = status
        self.tracking_number = tracking_number
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()