from datetime import datetime
from typing import List, Optional


class OrderItem:
    def __init__(self, product_id: str, quantity: int, price: float, size: str, color: str):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.size = size
        self.color = color

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        return cls(
            product_id=str(data.get('product_id')),
            quantity=int(data.get('quantity')),
            price=float(data.get('price')),
            size=data.get('size', ''),
            color=data.get('color', '')
        )


class Order:
    def __init__(self, user_id: str, items: List[OrderItem], total_amount: float, shipping_address: dict,
                 payment_method: str, delivery_method: str, delivery_cost: float, status: str = "processing",
                 tracking_number: Optional[str] = None, notes: Optional[str] = None, _id: Optional[str] = None):
        self._id = _id
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

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        # Припускаємо, що data['items'] — список словників, які треба конвертувати в OrderItem
        items_data = data.get('items', [])
        items = [OrderItem.from_dict(item) for item in items_data]

        # Дата створення та оновлення — конвертуємо з рядка або обʼєкта datetime, якщо потрібно
        created_at = data.get('created_at')
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        updated_at = data.get('updated_at')
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        order = cls(
            user_id=str(data.get('user_id')),
            items=items,
            total_amount=data.get('total_amount'),
            shipping_address=data.get('shipping_address'),
            payment_method=data.get('payment_method'),
            delivery_method=data.get('delivery_method'),
            delivery_cost=data.get('delivery_cost'),
            status=data.get('status', 'processing'),
            tracking_number=data.get('tracking_number'),
            notes=data.get('notes'),
            _id=data.get('_id')
        )
        # Якщо потрібно, встановлюємо created_at і updated_at явно (перезаписуємо поле)
        if created_at:
            order.created_at = created_at
        if updated_at:
            order.updated_at = updated_at

        # Ініціалізація payment_status (якщо потрібно брати з data)
        if 'payment_status' in data:
            order.payment_status = data['payment_status']

        return order
