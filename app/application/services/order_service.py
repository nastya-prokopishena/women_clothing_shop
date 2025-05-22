# app/application/services/order_service.py
from app.domain.models.order import Order, OrderItem
from app.infrastructure.persistence.order_repository import OrderRepository
from app.infrastructure.persistence.product_repository import ProductRepository
from app.infrastructure.persistence.cart_repository import CartRepository  # Потрібен для очищення кошика
from datetime import datetime
from flask import current_app  # Для логування
from typing import Optional, List, Tuple


class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()
        self.product_repo = ProductRepository()
        self.cart_repo = CartRepository()  # Ініціалізуємо репозиторій кошика

    def create_order(self, user_id: Optional[str], shipping_address: dict, payment_method: str,
                     cart_items: List[dict], subtotal: float,
                     delivery_price: float, total_order_amount: float) -> Tuple[bool, str, Optional[str]]:
        """
        Створює нове замовлення.
        """
        if not cart_items:
            return False, "Кошик порожній, неможливо створити замовлення.", None

        order_items_models: List[OrderItem] = []

        # 1. Перевірка наявності товарів та формування OrderItem
        for item_data in cart_items:
            product = self.product_repo.get_product_by_id(item_data['product_id'])
            if not product or not hasattr(product, 'stock'):
                log_msg = f"Товар {item_data.get('product_name', 'N/A')} (ID: {item_data['product_id']}) не знайдено або немає інформації про залишки."
                if current_app:
                    current_app.logger.error(log_msg)
                else:
                    print(f"ERROR: {log_msg}")
                return False, f"Товар '{item_data.get('product_name', 'N/A')}' більше не доступний.", None

            if product.stock < item_data['quantity']:
                log_msg = f"Недостатньо товару {product.name} (ID: {product.product_id}). Замовлено: {item_data['quantity']}, на складі: {product.stock}"
                if current_app:
                    current_app.logger.warning(log_msg)
                else:
                    print(f"WARNING: {log_msg}")
                return False, f"На жаль, товару '{product.name}' недостатньо на складі ({product.stock} од.). Будь ласка, оновіть кошик.", None

            order_item = OrderItem(
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                size=item_data.get('size'),
                color=item_data.get('color')
            )
            order_items_models.append(order_item)

        # 2. Зменшуємо кількість на складі
        products_to_revert_stock = []
        for item_model in order_items_models:
            success_stock_update = self.product_repo.decrease_stock(item_model.product_id, item_model.quantity)
            if not success_stock_update:
                for reverted_item in products_to_revert_stock:
                    self.product_repo.decrease_stock(reverted_item['id'], -reverted_item['qty'])

                log_msg = f"КРИТИЧНО: Не вдалося зменшити залишок для товару ID: {item_model.product_id}."
                if current_app:
                    current_app.logger.error(log_msg)
                else:
                    print(f"ERROR: {log_msg}")
                return False, "Виникла помилка при оновленні залишків на складі. Спробуйте пізніше.", None
            products_to_revert_stock.append({'id': item_model.product_id, 'qty': item_model.quantity})

        # 3. Створюємо об'єкт замовлення БЕЗ customer_details
        new_order = Order(
            user_id=user_id,
            items=order_items_models,
            total_amount=total_order_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            delivery_method="Нова Пошта",
            delivery_cost=delivery_price,
            status="pending_payment" if payment_method != "cash_on_delivery" else "processing"
            # created_at, updated_at, payment_status, subtotal_amount - ініціалізуються в моделі Order
        )
        # new_order = Order(
        #     user_id=user_id,
        #     items=order_items_models,
        #     total_amount=total_order_amount,
        #     shipping_address=shipping_address,
        #     payment_method=payment_method,
        #     delivery_method="Нова Пошта",
        #     delivery_cost=delivery_price,
        #     status="pending_payment" if payment_method != "cash_on_delivery" else "processing"
        # )

        try:
            order_id = self.order_repo.save(new_order)
            # Якщо потрібно відправити email, customer_details (з форми) передаються сюди з маршруту
            # і використовуються для виклику EmailService
            return True, "Замовлення успішно створено!", order_id
        except Exception as e:
            for reverted_item in products_to_revert_stock:
                try:
                    self.product_repo.decrease_stock(reverted_item['id'], -reverted_item['qty'])
                except Exception as stock_revert_error:
                    if current_app: current_app.logger.critical(
                        f"CRITICAL: Failed to revert stock for product {reverted_item['id']} after order save failure: {stock_revert_error}")

            log_msg = f"Помилка при збереженні замовлення: {e}"
            if current_app:
                current_app.logger.error(log_msg)
            else:
                print(f"ERROR: {log_msg}")
            return False, "Не вдалося зберегти ваше замовлення. Будь ласка, спробуйте пізніше.", None

    def get_order_details_for_confirmation(self, order_id: str) -> Optional[Order]:
        return self.order_repo.get_by_id(order_id)

    def get_orders_by_user_id(self, user_id: str) -> List[Order]:
        return self.order_repo.get_orders_by_user_id(user_id)
