# app/infrastructure/persistence/order_repository.py
from bson import ObjectId
from app.extensions import mongo
from app.domain.models.order import Order, OrderItem  # Ваші доменні моделі
from datetime import datetime
from typing import Optional, List


class OrderRepository:
    def __init__(self):
        self.collection = mongo.db.orders  # Колекція для замовлень

    def _order_item_to_dict(self, item: OrderItem) -> dict:
        return {
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': item.price,
            'size': item.size,
            'color': item.color,
        }

    def _map_to_order_item(self, data: dict) -> OrderItem:
        return OrderItem(
            product_id=str(data.get('product_id')),
            quantity=data.get('quantity'),
            price=data.get('price'),
            size=data.get('size'),
            color=data.get('color'),
        )

    def save(self, order: Order) -> str:
        """Зберігає нове замовлення в базу даних та повертає його ID."""
        order_doc = {
            'user_id': str(order.user_id),  # Припускаємо, що модель Order обробляє ObjectId або None
            'items': [self._order_item_to_dict(item) for item in order.items],
            'total_amount': order.total_amount,
            # 'subtotal_amount': order.subtotal_amount, # Якщо subtotal_amount є в моделі Order
            # і ви хочете його зберігати, розкоментуйте.
            # Ваша модель Order розраховує його, тому зберігати його тут
            # може бути надлишковим, якщо ви завжди його розраховуєте при завантаженні.
            'shipping_address': order.shipping_address,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status,
            'delivery_method': order.delivery_method,
            'delivery_cost': order.delivery_cost,
            'status': order.status,
            'tracking_number': order.tracking_number,
            'notes': order.notes,
            'created_at': order.created_at,
            'updated_at': datetime.utcnow()
        }

        # Додаємо subtotal_amount, якщо він є атрибутом об'єкта order,
        # навіть якщо його немає в __init__
        if hasattr(order, 'subtotal_amount'):
            order_doc['subtotal_amount'] = order.subtotal_amount
        else:
            # Якщо його немає і ви не хочете зберігати, можна нічого не робити
            # або розрахувати тут, якщо потрібно для запису в БД
            order_doc['subtotal_amount'] = sum(item.price * item.quantity for item in order.items)

        result = self.collection.insert_one(order_doc)
        return str(result.inserted_id)

    def get_by_id(self, _id: str) -> Optional[Order]:
        """Отримує замовлення за його ID."""
        if not ObjectId.is_valid(_id):
            return None
        data = self.collection.find_one({'_id': ObjectId(_id)})
        if not data:
            return None

        items = [self._map_to_order_item(item_data) for item_data in data.get('items', [])]

        # Створюємо об'єкт Order, передаючи тільки ті аргументи,
        # які є в конструкторі Order.__init__
        # Зверніть увагу на імена параметрів у конструкторі Order
        order_instance = Order(
            # _id=data.get('_id'), # Якщо ваш __init__ приймає _id, інакше він генерується в моделі
            # Ваша остання модель Order генерує _id сама, якщо не передано.
            # Але для відтворення з БД краще передати існуючий _id.
            # Щоб це працювало, _id має бути першим параметром або параметром за замовчуванням у __init__
            # або ж ви встановлюєте self._id = _id if _id else ObjectId() всередині __init__.
            # ВАША МОДЕЛЬ: _id=None в __init__ і self._id = _id if _id else ObjectId() - це ОК.
            # Тому передаємо _id=data.get('_id')
            order_id=data.get('_id'),
            user_id=str(data.get('user_id')) if data.get('user_id') else None,
            items=items,
            total_amount=data.get('total_amount'),
            shipping_address=data.get('shipping_address'),
            payment_method=data.get('payment_method'),
            delivery_method=data.get('delivery_method', "Нова Пошта"),  # Значення за замовчуванням, якщо немає в БД
            delivery_cost=data.get('delivery_cost', 0.0),  # Значення за замовчуванням
            status=data.get('status', "processing"),  # Значення за замовчуванням
            tracking_number=data.get('tracking_number'),
            notes=data.get('notes')
            # customer_details=data.get('customer_details'), # ВИДАЛЕНО
            # created_at=data.get('created_at'), # Якщо __init__ не приймає created_at/updated_at
            # updated_at=data.get('updated_at')
        )

        # Якщо created_at та updated_at не встановлюються через __init__ при завантаженні,
        # а мають бути взяті з БД:
        if order_instance and data.get('created_at'):
            order_instance.created_at = data.get('created_at')
        if order_instance and data.get('updated_at'):
            order_instance.updated_at = data.get('updated_at')

        # Якщо payment_status не встановлюється через __init__ при завантаженні:
        if order_instance and data.get('payment_status'):
            order_instance.payment_status = data.get('payment_status')

        # Якщо subtotal_amount зберігається в БД і не розраховується в __init__ при завантаженні:
        # if order_instance and data.get('subtotal_amount') is not None: # Перевірка на None, бо може бути 0.0
        #    order_instance.subtotal_amount = data.get('subtotal_amount')
        # Або якщо він завжди розраховується в __init__ моделі Order, то цей блок не потрібен.

        return order_instance

    def get_orders_by_user_id(self, user_id: str) -> List[Order]:
        """Повертає список замовлень користувача за user_id."""
        orders_data = self.collection.find({'user_id': user_id}).sort('created_at', -1)
        orders = []

        for data in orders_data:
            items = [self._map_to_order_item(item_data) for item_data in data.get('items', [])]
            order = Order(
                _id=data.get('_id'),
                user_id=str(data.get('user_id')) if data.get('user_id') else None,
                items=items,
                total_amount=data.get('total_amount'),
                shipping_address=data.get('shipping_address'),
                payment_method=data.get('payment_method'),
                delivery_method=data.get('delivery_method', "Нова Пошта"),
                delivery_cost=data.get('delivery_cost', 0.0),
                status=data.get('status', "processing"),
                tracking_number=data.get('tracking_number'),
                notes=data.get('notes')
            )
            if data.get('created_at'):
                order.created_at = data.get('created_at')
            if data.get('updated_at'):
                order.updated_at = data.get('updated_at')
            if data.get('payment_status'):
                order.payment_status = data.get('payment_status')

            orders.append(order)

        return orders
