# tests/test_cart_views.py
import unittest
from urllib.parse import urlparse  # For parsing URL
from flask import url_for, session, flash
from flask_testing import TestCase
from app import create_app
from unittest.mock import patch, ANY  # ANY для перевірки частини аргументів

from app.domain.models.product import Product, ProductAttribute


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key-cart-view'
        app.config['SERVER_NAME'] = 'localhost.localdomain'
        app.config['APPLICATION_ROOT'] = '/'
        app.config['PREFERRED_URL_SCHEME'] = 'http'
        return app

    def setUp(self):
        self.sample_product_attributes = ProductAttribute(
            colors=["red", "blue"],
            sizes=["S", "M"],
            material="cotton"
        )
        self.sample_product_1 = Product(
            product_id="prod_cart_1", name="Cart Test Product 1", price=150.00, stock=10,
            images=["cart_img1.jpg"], category_id="cat_cart", description="DescCart1", care="CareCart1",
            attributes=self.sample_product_attributes
        )
        self.sample_product_2 = Product(  # Додамо другий продукт
            product_id="prod_cart_2", name="Cart Test Product 2", price=200.00, stock=5,
            images=["cart_img2.jpg"], category_id="cat_cart_alt", description="DescCart2", care="CareCart2",
            attributes=self.sample_product_attributes
        )

    def tearDown(self):
        with self.app.app_context():
            keys_to_pop = ['user_id', 'session_id', '_flashes']
            for key in keys_to_pop:
                if key in session:
                    session.pop(key, None)


class CartViewTests(BaseTestCase):

    def test_view_empty_cart_page_displays_correctly(self):
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_cart_service_instance = MockCartService.return_value
            mock_cart_service_instance.get_cart_display_data.return_value = {'items': [], 'total_amount': 0.0}
            response = self.client.get(url_for('cart_bp.view_cart_page'))
            response_text = response.data.decode('utf-8')
            self.assertEqual(response.status_code, 200)
            self.assertIn("Ваш кошик", response_text)
            self.assertIn("Ваш кошик порожній.", response_text)
            self.assertNotIn("Підсумок кошика", response_text)
            mock_cart_service_instance.get_cart_display_data.assert_called_once()

    def test_view_cart_page_with_items_displays_correctly(self):
        cart_item_display_data = {
            'product_id': self.sample_product_1.product_id,
            'product_name': self.sample_product_1.name,
            'product_image': self.sample_product_1.images[0] if self.sample_product_1.images else 'placeholder.jpg',
            'size': 'S', 'color': 'red', 'price': self.sample_product_1.price,
            'quantity': 2, 'total_price': self.sample_product_1.price * 2
        }
        test_cart_data = {
            'items': [cart_item_display_data],
            'total_amount': self.sample_product_1.price * 2
        }
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_cart_service_instance = MockCartService.return_value
            mock_cart_service_instance.get_cart_display_data.return_value = test_cart_data
            response = self.client.get(url_for('cart_bp.view_cart_page'))
            response_text = response.data.decode('utf-8')
            self.assertEqual(response.status_code, 200)
            self.assertIn("Ваш кошик", response_text)
            self.assertIn(self.sample_product_1.name, response_text)
            self.assertIn("Підсумок кошика", response_text)
            self.assertNotIn("Ваш кошик порожній.", response_text)
            mock_cart_service_instance.get_cart_display_data.assert_called_once()

    def test_add_to_cart_success_redirects_to_cart_page(self):
        form_data_to_add = {
            'product_id': self.sample_product_1.product_id,
            'quantity': 1,
            'color': 'red',
            'size': 'S'
        }
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_cart_service_instance = MockCartService.return_value
            mock_cart_service_instance.add_product_to_cart.return_value = (True, "Товар успішно додано!")
            response = self.client.post(url_for('cart_bp.add_to_cart'), data=form_data_to_add, follow_redirects=False)
            mock_cart_service_instance.add_product_to_cart.assert_called_once()
            self.assertEqual(response.status_code, 302)
            expected_path = url_for('cart_bp.view_cart_page', _external=False)
            self.assertEqual(urlparse(response.location).path, expected_path)
            with self.client.session_transaction() as sess:
                flashed_messages = dict(sess.get('_flashes', []))
            self.assertIn("success", flashed_messages)
            self.assertIn("Товар успішно додано!", flashed_messages.get("success", ""))

    def test_add_to_cart_failure_redirects_and_flashes_error(self):
        form_data_to_add = {
            'product_id': 'non_existent_product',
            'quantity': 1
        }
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_cart_service_instance = MockCartService.return_value
            mock_cart_service_instance.add_product_to_cart.return_value = (False, "Товар не знайдено.")
            response = self.client.post(url_for('cart_bp.add_to_cart'), data=form_data_to_add, follow_redirects=False)
            mock_cart_service_instance.add_product_to_cart.assert_called_once()
            self.assertEqual(response.status_code, 302)
            expected_path = url_for('cart_bp.view_cart_page', _external=False)
            self.assertEqual(urlparse(response.location).path, expected_path)
            with self.client.session_transaction() as sess:
                flashed_messages = dict(sess.get('_flashes', []))
            self.assertIn("error", flashed_messages)
            self.assertIn("Товар не знайдено.", flashed_messages.get("error", ""))

    def test_remove_from_cart_success_redirects_to_cart_page(self):
        form_data_to_remove = {
            'product_id': self.sample_product_1.product_id,
            'size': 'S',
            'color': 'red'
        }
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_cart_service_instance = MockCartService.return_value
            mock_cart_service_instance.remove_product_from_cart.return_value = (True, "Товар успішно видалено!")
            response = self.client.post(url_for('cart_bp.remove_from_cart'), data=form_data_to_remove,
                                        follow_redirects=False)
            mock_cart_service_instance.remove_product_from_cart.assert_called_once()
            self.assertEqual(response.status_code, 302)
            expected_path = url_for('cart_bp.view_cart_page', _external=False)
            self.assertEqual(urlparse(response.location).path, expected_path)
            with self.client.session_transaction() as sess:
                flashed_messages = dict(sess.get('_flashes', []))
            self.assertIn("success", flashed_messages)
            self.assertIn("Товар успішно видалено!", flashed_messages.get("success", ""))

    # --- НОВІ 5 ТЕСТІВ ---

    def test_remove_from_cart_item_not_in_cart(self):
        """
        Тест: Спроба видалити товар, якого немає в кошику.
        """
        form_data_to_remove = {'product_id': 'prod_not_in_cart', 'size': 'M', 'color': 'Black'}
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_service_instance = MockCartService.return_value
            mock_service_instance.remove_product_from_cart.return_value = (False, "Товар не знайдено у кошику.")

            response = self.client.post(url_for('cart_bp.remove_from_cart'), data=form_data_to_remove)

            self.assertEqual(response.status_code, 302)  # Очікуємо редирект назад на кошик
            expected_path = url_for('cart_bp.view_cart_page', _external=False)
            self.assertEqual(urlparse(response.location).path, expected_path)
            mock_service_instance.remove_product_from_cart.assert_called_once()
            with self.client.session_transaction() as sess:
                flashed_messages = dict(sess.get('_flashes', []))
            self.assertIn("error", flashed_messages)
            self.assertIn("Товар не знайдено у кошику.", flashed_messages.get("error", ""))

    def test_add_to_cart_creates_session_id_for_guest(self):
        """
        Тест: Створення session_id для гостя при першому додаванні товару.
        """
        form_data = {'product_id': self.sample_product_1.product_id, 'quantity': 1, 'color': 'red', 'size': 'S'}
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_service_instance = MockCartService.return_value
            mock_service_instance.add_product_to_cart.return_value = (True, "Товар додано")

            # Переконуємося, що сесія порожня від 'user_id' та 'session_id'
            with self.client.session_transaction() as sess:
                sess.pop('user_id', None)
                sess.pop('session_id', None)

            self.client.post(url_for('cart_bp.add_to_cart'), data=form_data)

            # Перевіряємо, що session_id було створено і передано в сервіс
            # ANY означає, що ми очікуємо будь-яке значення для session_id, оскільки воно генерується
            mock_service_instance.add_product_to_cart.assert_called_with(
                user_id=None, session_id=ANY, product_id=self.sample_product_1.product_id,
                quantity=1, color='red', size='S'
            )
            # Перевіряємо, що session_id тепер є в сесії Flask
            with self.client.session_transaction() as sess:
                self.assertIsNotNone(sess.get('session_id'))

    def test_add_to_cart_uses_user_id_when_logged_in(self):
        """
        Тест: Використання user_id при додаванні товару залогіненим користувачем.
        """
        form_data = {'product_id': self.sample_product_1.product_id, 'quantity': 1, 'color': 'red', 'size': 'S'}
        test_user_id = "user123"
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_service_instance = MockCartService.return_value
            mock_service_instance.add_product_to_cart.return_value = (True, "Товар додано")

            with self.client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess.pop('session_id', None)  # Переконуємося, що немає гостьового ID

            self.client.post(url_for('cart_bp.add_to_cart'), data=form_data)

            mock_service_instance.add_product_to_cart.assert_called_with(
                user_id=test_user_id, session_id=None, product_id=self.sample_product_1.product_id,
                quantity=1, color='red', size='S'
            )

    def test_view_cart_page_uses_user_id_when_logged_in(self):
        """
        Тест: Сторінка кошика використовує user_id для залогіненого користувача.
        """
        test_user_id = "user456"
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_service_instance = MockCartService.return_value
            mock_service_instance.get_cart_display_data.return_value = {'items': [], 'total_amount': 0.0}

            with self.client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess.pop('session_id', None)

            self.client.get(url_for('cart_bp.view_cart_page'))

            mock_service_instance.get_cart_display_data.assert_called_once_with(user_id=test_user_id, session_id=None)

    def test_view_cart_page_uses_session_id_when_guest(self):
        """
        Тест: Сторінка кошика використовує session_id для гостя.
        """
        test_session_id = "guest_session_xyz"
        with patch('app.web.routes.cart.CartService') as MockCartService:
            mock_service_instance = MockCartService.return_value
            mock_service_instance.get_cart_display_data.return_value = {'items': [], 'total_amount': 0.0}

            with self.client.session_transaction() as sess:
                sess.pop('user_id', None)
                sess['session_id'] = test_session_id

            self.client.get(url_for('cart_bp.view_cart_page'))

            mock_service_instance.get_cart_display_data.assert_called_once_with(user_id=None,
                                                                                session_id=test_session_id)

# if __name__ == '__main__':
#     unittest.main()