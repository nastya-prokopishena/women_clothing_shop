from bson import ObjectId
from app.extensions import mongo # Ваш екземпляр Mongo
from app.domain.models.cart import Cart, CartItem # Ваші доменні моделі
from datetime import datetime
from typing import Optional, List

class CartRepository:
    def __init__(self):
        self.collection = mongo.db.carts # Назва колекції для кошиків

    def _map_to_cart_item(self, data: dict) -> CartItem:
        """Мапить словник з бази даних на об'єкт CartItem."""
        return CartItem(
            product_id=str(data.get('product_id')), # Зберігаємо як рядок, якщо в БД ObjectId
            quantity=data.get('quantity'),
            size=data.get('size'),
            color=data.get('color'),
            # added_at можна не мапити, якщо воно встановлюється при створенні CartItem
            # або мапити, якщо ви його зберігаєте і хочете відновити
        )

    def _map_to_cart(self, data: dict) -> Cart:
        """Мапить словник з бази даних на об'єкт Cart."""
        if not data:
            return None
        items_data = data.get('items', [])
        items = [self._map_to_cart_item(item_data) for item_data in items_data]
        return Cart(
            user_id=str(data.get('user_id')) if data.get('user_id') else None,
            session_id=data.get('session_id'),
            items=items,
            coupon_code=data.get('coupon_code'),
            discount_amount=data.get('discount_amount', 0.0),
            # _id та last_updated можна не передавати сюди,
            # якщо вони керуються на рівні моделі або при збереженні
            # last_updated=data.get('last_updated')
        )

    def _cart_item_to_dict(self, item: CartItem) -> dict:
        """Конвертує об'єкт CartItem у словник для збереження в БД."""
        return {
            'product_id': item.product_id, # Можливо, ObjectId(item.product_id), якщо product_id - це ObjectId в колекції products
            'quantity': item.quantity,
            'size': item.size,
            'color': item.color,
            'added_at': item.added_at
        }

    def _cart_to_dict(self, cart: Cart) -> dict:
        """Конвертує об'єкт Cart у словник для збереження в БД."""
        data = {
            'items': [self._cart_item_to_dict(item) for item in cart.items],
            'coupon_code': cart.coupon_code,
            'discount_amount': cart.discount_amount,
            'last_updated': datetime.utcnow() # Завжди оновлюємо час останньої зміни
        }
        if cart.user_id:
            data['user_id'] = ObjectId(cart.user_id) if ObjectId.is_valid(cart.user_id) else cart.user_id
        if cart.session_id:
            data['session_id'] = cart.session_id
        return data

    def get_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Optional[Cart]:
        """
        Отримує кошик за user_id або session_id.
        Якщо обидва надані, user_id має пріоритет.
        """
        query = {}
        if user_id:
            if ObjectId.is_valid(user_id):
                query['user_id'] = ObjectId(user_id)
            else:
                # Якщо user_id не є валідним ObjectId, можливо, це помилка або інший тип ID
                # Тут можна додати логування або обробку помилки
                return None
        elif session_id:
            query['session_id'] = session_id
        else:
            return None # Немає ідентифікатора для пошуку

        cart_data = self.collection.find_one(query)
        return self._map_to_cart(cart_data) if cart_data else None

    def create_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Cart:
        """Створює новий порожній кошик."""
        new_cart = Cart(user_id=user_id, session_id=session_id)
        cart_dict = self._cart_to_dict(new_cart)

        # Видаляємо None значення перед вставкою, якщо вони не потрібні в БД
        cart_dict_cleaned = {k: v for k, v in cart_dict.items() if v is not None}
        if 'user_id' not in cart_dict_cleaned and 'session_id' not in cart_dict_cleaned:
            raise ValueError("Cart must have either user_id or session_id to be created")


        result = self.collection.insert_one(cart_dict_cleaned)
        # Встановлюємо _id для об'єкта Cart, хоча для логіки отримання це може бути не обов'язково,
        # оскільки ми шукаємо за user_id/session_id.
        # new_cart._id = result.inserted_id # Якщо модель Cart має поле _id
        return new_cart


    def save_cart(self, cart: Cart) -> None:
        """
        Зберігає або оновлює кошик в базі даних.
        Використовує user_id або session_id для ідентифікації кошика.
        """
        cart_dict = self._cart_to_dict(cart)
        query = {}

        if cart.user_id:
            if ObjectId.is_valid(cart.user_id):
                query['user_id'] = ObjectId(cart.user_id)
            else:
                # Обробка помилки або логування
                return
        elif cart.session_id:
            query['session_id'] = cart.session_id
        else:
            # Кошик без ідентифікатора не може бути збережений таким чином
            raise ValueError("Cart must have either user_id or session_id to be saved")

        # Використовуємо upsert=True, щоб створити документ, якщо він не існує
        self.collection.update_one(query, {'$set': cart_dict}, upsert=True)

    def delete_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> None:
        """Видаляє кошик."""
        query = {}
        if user_id:
            if ObjectId.is_valid(user_id):
                query['user_id'] = ObjectId(user_id)
            else:
                return
        elif session_id:
            query['session_id'] = session_id
        else:
            return

        self.collection.delete_one(query)
