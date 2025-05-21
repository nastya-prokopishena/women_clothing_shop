# app/application/services/cart_services.py

from app.infrastructure.persistence.cart_repository import CartRepository
from app.infrastructure.persistence.product_repository import ProductRepository
from app.domain.models.cart import CartItem, Cart  # Переконайтеся, що Cart теж імпортовано
from flask import current_app  # Для логування (опціонально)


class CartService:
    def __init__(self):
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()

    def get_cart_display_data(self, user_id=None, session_id=None):
        """
        Отримує дані кошика для відображення, включаючи деталі товарів.
        """
        cart = self.cart_repo.get_cart(user_id=user_id, session_id=session_id)

        if not cart or not cart.items:
            return {'items': [], 'total_amount': 0.0}

        detailed_items = []
        total_cart_amount = 0.0

        for cart_item_obj in cart.items:  # cart.items - це список об'єктів CartItem
            product = self.product_repo.get_product_by_id(cart_item_obj.product_id)

            if product:
                item_total_price = product.price * cart_item_obj.quantity
                detailed_items.append({
                    'product_id': cart_item_obj.product_id,
                    'product_name': product.name,
                    'product_image': product.images[0] if product.images else None,
                    'size': cart_item_obj.size,
                    'color': cart_item_obj.color,
                    'price': product.price,  # Ціна за одиницю
                    'quantity': cart_item_obj.quantity,
                    'total_price': item_total_price
                })
                total_cart_amount += item_total_price
            else:
                # Логуємо, якщо товар з кошика не знайдено в каталозі
                if current_app:  # Перевірка, чи є контекст додатку для логування
                    current_app.logger.warning(
                        f"Product with ID {cart_item_obj.product_id} found in cart but not in product repository.")
                else:  # Якщо немає контексту додатку (наприклад, при тестах поза контекстом)
                    print(f"Warning: Product with ID {cart_item_obj.product_id} not found in product repository.")

        return {
            'items': detailed_items,
            'total_amount': total_cart_amount
        }

    def add_product_to_cart(self, user_id, session_id, product_id, quantity, color, size):
        """
        Додає товар до кошика або оновлює його кількість.
        Повертає (True, "Повідомлення про успіх") або (False, "Повідомлення про помилку").
        """
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            return False, "Товар не знайдено."

        # Перевірка наявності атрибуту 'stock' у моделі Product
        if not hasattr(product, 'stock'):
            if current_app:
                current_app.logger.error(f"Product model for ID {product_id} does not have a 'stock' attribute.")
            else:
                print(f"ERROR: Product model for ID {product_id} does not have a 'stock' attribute.")
            return False, "Помилка на сервері: неможливо перевірити наявність товару."

        if product.stock < quantity:
            return False, f"На жаль, товару '{product.name}' залишилося лише {product.stock} од."

        # Визначаємо, чи шукати/створювати кошик для користувача чи для сесії
        current_user_id = user_id if user_id else None
        current_session_id = session_id if not user_id else None

        cart = self.cart_repo.get_cart(user_id=current_user_id, session_id=current_session_id)
        if not cart:
            cart = self.cart_repo.create_cart(user_id=current_user_id, session_id=current_session_id)

        existing_item = None
        for item_in_cart in cart.items:
            if item_in_cart.product_id == product_id and item_in_cart.size == size and item_in_cart.color == color:
                existing_item = item_in_cart
                break

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if product.stock < new_quantity:
                return False, f"Не вдалося додати бажану кількість товару '{product.name}'. Залишилося {product.stock} од., а у вас вже {existing_item.quantity} в кошику."
            existing_item.quantity = new_quantity
        else:
            new_item = CartItem(
                product_id=product_id,
                quantity=quantity,
                size=size,
                color=color
                # price=product.price # Можна зберігати ціну тут на момент додавання
            )
            cart.items.append(new_item)

        try:
            self.cart_repo.save_cart(cart)
            return True, f"Товар '{product.name}' успішно додано до кошика!"
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error saving cart in add_product_to_cart: {e}")
            else:
                print(f"Error saving cart in add_product_to_cart: {e}")
            return False, "Не вдалося зберегти кошик. Спробуйте пізніше."

    def remove_product_from_cart(self, user_id, session_id, product_id, size, color):
        """
        Видаляє товар (визначений за product_id, size, color) з кошика.
        Повертає (True, "Повідомлення про успіх") або (False, "Повідомлення про помилку").
        """
        current_user_id = user_id if user_id else None
        current_session_id = session_id if not user_id else None

        cart = self.cart_repo.get_cart(user_id=current_user_id, session_id=current_session_id)

        if not cart or not cart.items:
            return False, "Кошик не знайдено або він порожній."

        initial_items_count = len(cart.items)

        # Створюємо новий список, виключаючи товар, що видаляється
        cart.items = [
            item for item in cart.items
            if not (item.product_id == product_id and item.size == size and item.color == color)
        ]

        if len(cart.items) < initial_items_count:
            try:
                self.cart_repo.save_cart(cart)
                return True, f"Товар успішно видалено з кошика."
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Error saving cart in remove_product_from_cart: {e}")
                else:
                    print(f"Error saving cart in remove_product_from_cart: {e}")
                # Потенційно, якщо збереження не вдалося, варто повернути товари назад у cart.items
                # але це ускладнює логіку. Поки що просто повідомляємо про помилку.
                return False, "Не вдалося оновити кошик після видалення товару."
        else:
            return False, "Товар не знайдено у вашому кошику для видалення."

    def merge_guest_cart_to_user(self, guest_session_id: str, user_id: str):
        """
        Об'єднує товари з гостьового кошика (за guest_session_id)
        до кошика зареєстрованого користувача (за user_id).
        Після успішного об'єднання гостьовий кошик видаляється.
        """
        guest_cart = self.cart_repo.get_cart(session_id=guest_session_id)

        if not guest_cart:
            return True  # Немає гостьового кошика для об'єднання
        if not guest_cart.items:
            self.cart_repo.delete_cart(session_id=guest_session_id)  # Видаляємо порожній гостьовий кошик
            return True

        user_cart = self.cart_repo.get_cart(user_id=user_id)

        if not user_cart:
            # У користувача немає свого кошика, створюємо новий і копіюємо товари
            user_cart = self.cart_repo.create_cart(user_id=user_id)
            for guest_item in guest_cart.items:  # Просто копіюємо, перевірки на склад вже були при додаванні
                user_cart.items.append(guest_item)
            # Можна також перенести coupon_code та discount_amount, якщо потрібно
            user_cart.coupon_code = guest_cart.coupon_code
            user_cart.discount_amount = guest_cart.discount_amount
        else:
            # У користувача вже є свій кошик, об'єднуємо товари
            for guest_item in guest_cart.items:
                product = self.product_repo.get_product_by_id(guest_item.product_id)
                if not product:
                    if current_app:
                        current_app.logger.warning(f"При об'єднанні: товар ID {guest_item.product_id} не знайдено.")
                    else:
                        print(f"Warning: Product ID {guest_item.product_id} not found during merge.")
                    continue

                existing_item_in_user_cart = None
                for user_item in user_cart.items:
                    if (user_item.product_id == guest_item.product_id and
                            user_item.size == guest_item.size and
                            user_item.color == guest_item.color):
                        existing_item_in_user_cart = user_item
                        break

                if existing_item_in_user_cart:
                    new_quantity = existing_item_in_user_cart.quantity + guest_item.quantity
                    if hasattr(product, 'stock'):
                        if product.stock >= new_quantity:
                            existing_item_in_user_cart.quantity = new_quantity
                        else:
                            existing_item_in_user_cart.quantity = product.stock
                            if current_app:
                                current_app.logger.info(
                                    f"Об'єднання: кількість для {product.name} обмежена залишком {product.stock}.")
                            else:
                                print(f"Merge: Quantity for {product.name} limited by stock {product.stock}.")
                    else:  # Якщо немає атрибуту stock
                        existing_item_in_user_cart.quantity = new_quantity
                else:
                    if hasattr(product, 'stock'):
                        if product.stock >= guest_item.quantity:
                            user_cart.items.append(guest_item)
                        else:
                            if current_app:
                                current_app.logger.info(
                                    f"Об'єднання: товар {product.name} не додано, недостатньо на складі ({guest_item.quantity} > {product.stock}).")
                            else:
                                print(
                                    f"Merge: Item {product.name} not added, insufficient stock ({guest_item.quantity} > {product.stock}).")
                    else:  # Якщо немає атрибуту stock
                        user_cart.items.append(guest_item)

        try:
            self.cart_repo.save_cart(user_cart)
            self.cart_repo.delete_cart(session_id=guest_session_id)
            return True
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Помилка при збереженні/видаленні кошиків під час об'єднання: {e}")
            else:
                print(f"Error saving/deleting carts during merge: {e}")
            return False

    def clear_cart(self, user_id=None, session_id=None):
        """
        Очищує кошик (видаляє всі товари з нього).
        """
        current_user_id = user_id if user_id else None
        current_session_id = session_id if not user_id else None

        cart = self.cart_repo.get_cart(user_id=current_user_id, session_id=current_session_id)
        if cart:
            cart.items = []  # Очищуємо список товарів
            cart.coupon_code = None  # Скидаємо купон
            cart.discount_amount = 0.0  # Скидаємо знижку
            try:
                self.cart_repo.save_cart(cart)
                return True, "Кошик успішно очищено."
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Error clearing cart: {e}")
                else:
                    print(f"Error clearing cart: {e}")
                return False, "Не вдалося очистити кошик."
        return False, "Кошик не знайдено."

    # Тут можуть бути інші методи, наприклад, для оновлення кількості конкретного товару,
    # застосування купона тощо.
    # def update_cart_item_quantity(self, user_id, session_id, product_id, quantity, color, size):
    # ...