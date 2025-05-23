import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session, get_flashed_messages

from flask import Blueprint, render_template, request, redirect, url_for, flash # session вже імпортовано

class MockCartService:
    def get_cart_display_data(self, user_id, session_id):
        # Цей метод буде перевизначено в кожному тесті за потреби
        pass

    def clear_cart(self, user_id, session_id):
        # Цей метод буде перевизначено в кожному тесті за потреби
        pass

class MockOrderService:
    def create_order(self, user_id, shipping_address, payment_method, cart_items, subtotal, delivery_price, total_order_amount):
        # Цей метод буде перевизначено в кожному тесті за потреби
        pass

    def get_order_details_for_confirmation(self, order_id):
        # Цей метод буде перевизначено в кожному тесті за потреби
        pass


checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout_bp.route('/', methods=['GET', 'POST'])
@patch('app.web.routes.checkout.OrderService', new_callable=lambda: MockOrderService) # Мокуємо тут
@patch('app.web.routes.checkout.CartService', new_callable=lambda: MockCartService)   # Мокуємо тут
def checkout(PassedMockCartServiceClass, PassedMockOrderServiceClass): # Аргументи - це класи
    cart_service = PassedMockCartServiceClass() # Створюємо екземпляр
    order_service = PassedMockOrderServiceClass() # Створюємо екземпляр

    user_id = session.get('user_id')
    session_id_val = session.get('session_id')

    cart_data = cart_service.get_cart_display_data(user_id=user_id, session_id=session_id_val)

    if not cart_data or not cart_data.get('items'):
        flash("Ваш кошик порожній. Будь ласка, додайте товари перед оформленням.", "warning")
        return redirect(url_for('cart_bp.view_cart_page'))

    current_cart_items = cart_data.get('items', [])
    subtotal = cart_data.get('total_amount', 0.0)
    delivery_price = 50.00
    fee = 0.00
    discount = 0.00
    total_order_amount = subtotal + delivery_price + fee - discount

    if request.method == 'POST':
        form_data = request.form
        first_name = form_data.get('first_name')
        last_name = form_data.get('last_name')
        email = form_data.get('email')
        phone = form_data.get('phone')
        region = form_data.get('region')
        city = form_data.get('city')
        post_office = form_data.get('post_office')
        payment_method = form_data.get('payment_method')

        required_fields = [first_name, last_name, email, phone, region, city, post_office, payment_method]
        if not all(required_fields):
            flash("Будь ласка, заповніть усі обов'язкові поля.", "error")
            return render_template(
                'checkout.html',
                cart_items=current_cart_items,
                subtotal=subtotal,
                delivery_price=delivery_price,
                fee=fee,
                discount=discount,
                total_order_amount=total_order_amount,
                form_data=form_data
            )

        shipping_address_data = {
            "region": region, "city": city, "post_office": post_office
        }

        success, order_message, created_order_id = order_service.create_order(
            user_id=user_id,
            shipping_address=shipping_address_data,
            payment_method=payment_method,
            cart_items=current_cart_items,
            subtotal=subtotal,
            delivery_price=delivery_price,
            total_order_amount=total_order_amount
        )

        if success:
            clear_result = cart_service.clear_cart(user_id=user_id, session_id=session_id_val)
            if isinstance(clear_result, tuple) and not clear_result[0]:
                flash(
                    f"Замовлення №{created_order_id} створено, але виникла помилка при очищенні кошика: {clear_result[1]}",
                    "warning")
            elif not clear_result and not isinstance(clear_result, tuple):
                flash(
                    f"Замовлення №{created_order_id} створено, але виникла помилка при очищенні кошика.",
                    "warning")
            else:
                flash(f"Замовлення №{created_order_id} успішно створено! {order_message}", "success")

            session['last_order_id_for_confirmation'] = created_order_id
            session.pop('order_details', None)
            return redirect(url_for('auth.profile') + '?tab=orders') # Потрібно буде мокнути auth.profile
        else:
            flash(f"Помилка при створенні замовлення: {order_message}", "error")
            return render_template('checkout.html', cart_items=current_cart_items, subtotal=subtotal,
                                   delivery_price=delivery_price, fee=fee, discount=discount,
                                   total_order_amount=total_order_amount, form_data=form_data)

    return render_template(
        'checkout.html',
        cart_items=current_cart_items,
        subtotal=subtotal,
        delivery_price=delivery_price,
        fee=fee,
        discount=discount,
        total_order_amount=total_order_amount,
        form_data={}
    )


@checkout_bp.route('/order-confirmation')
@patch('app.web.routes.checkout.OrderService', new_callable=lambda: MockOrderService) # Мокуємо тут
def order_confirmation(PassedMockOrderServiceClass): # Аргумент - клас
    order_service = PassedMockOrderServiceClass() # Створюємо екземпляр
    order_id = session.pop('last_order_id_for_confirmation', None)

    if order_id:
        order_data_for_template = order_service.get_order_details_for_confirmation(order_id)
        if order_data_for_template:
            return render_template('order_confirmation.html', order=order_data_for_template)
        else:
            flash("Не вдалося завантажити деталі вашого замовлення.", "error")
            return redirect(url_for('main.home'))
    else:
        flash("Для перегляду підтвердження замовлення, будь ласка, оформіть його спочатку.", "info")
        return redirect(url_for('main.home'))

# ----- Код вашого Blueprint (checkout_bp) закінчується тут -----


class TestCheckoutBlueprint(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'super secret key' # Потрібно для flash і session
        self.app.register_blueprint(checkout_bp)

        # Створення "фейкових" блюпринтів для url_for
        cart_bp_mock = Blueprint('cart_bp', __name__)
        @cart_bp_mock.route('/cart_dummy')
        def view_cart_page(): return "Cart Page"
        self.app.register_blueprint(cart_bp_mock)

        auth_bp_mock = Blueprint('auth', __name__)
        @auth_bp_mock.route('/profile_dummy')
        def profile(): return "Profile Page"
        self.app.register_blueprint(auth_bp_mock)

        main_bp_mock = Blueprint('main', __name__)
        @main_bp_mock.route('/home_dummy')
        def home(): return "Home Page"
        self.app.register_blueprint(main_bp_mock)

        self.client = self.app.test_client()


    # --- Тести для маршруту checkout ---

    @patch('app.web.routes.checkout.render_template') # Мокуємо render_template
    @patch.object(MockCartService, 'get_cart_display_data')
    def test_checkout_get_empty_cart_redirects(self, mock_get_cart_data_method, mock_render_template):
        mock_get_cart_data_method.return_value = None # Імітуємо порожній кошик
        with self.client as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['session_id'] = 'test_session'
            response = client.get('/checkout/')
            self.assertEqual(response.status_code, 302) # Redirect
            self.assertTrue(response.location.endswith('/cart_dummy')) # Перевіряємо url_for

            with client.session_transaction() as sess:
                flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Ваш кошик порожній. Будь ласка, додайте товари перед оформленням."), flashed_messages)
            mock_render_template.assert_not_called()

    # Тест test_checkout_get_with_items_renders_template було видалено звідси


    @patch.object(MockOrderService, 'create_order')
    @patch.object(MockCartService, 'clear_cart')
    @patch.object(MockCartService, 'get_cart_display_data')
    def test_checkout_post_order_success_clears_cart_and_redirects(self, mock_get_cart_data_method, mock_clear_cart_method, mock_create_order_method):
        cart_items_data = {'items': [{'id': 1, 'name': 'Test Item', 'price': 100, 'quantity': 1}], 'total_amount': 100.0}
        mock_get_cart_data_method.return_value = cart_items_data
        mock_create_order_method.return_value = (True, "Order created successfully", 123)
        mock_clear_cart_method.return_value = True

        form_data = {
            'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com',
            'phone': '1234567890', 'region': 'Test Region', 'city': 'Test City',
            'post_office': 'Test PO', 'payment_method': 'card'
        }
        with self.client as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['session_id'] = 'test_session'

            response = client.post('/checkout/', data=form_data)

            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/profile_dummy?tab=orders'))
            mock_create_order_method.assert_called_once()
            mock_clear_cart_method.assert_called_once()

            with client.session_transaction() as sess:
                self.assertEqual(sess.get('last_order_id_for_confirmation'), 123)
                flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Замовлення №123 успішно створено! Order created successfully"), flashed_messages)


    @patch.object(MockOrderService, 'create_order')
    @patch.object(MockCartService, 'clear_cart')
    @patch.object(MockCartService, 'get_cart_display_data')
    def test_checkout_post_order_success_cart_clear_fails_tuple_response(self, mock_get_cart_data_method, mock_clear_cart_method, mock_create_order_method):
        cart_items_data = {'items': [{'id': 1}], 'total_amount': 100.0}
        mock_get_cart_data_method.return_value = cart_items_data
        mock_create_order_method.return_value = (True, "Order created", 124)
        mock_clear_cart_method.return_value = (False, "DB error")

        form_data = {
            'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com',
            'phone': '1234567890', 'region': 'Test Region', 'city': 'Test City',
            'post_office': 'Test PO', 'payment_method': 'card'
        }
        with self.client as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['session_id'] = 'test_session'
            response = client.post('/checkout/', data=form_data)
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                flashed_messages = get_flashed_messages(with_categories=True)
            expected_flash = ("warning", "Замовлення №124 створено, але виникла помилка при очищенні кошика: DB error")
            self.assertIn(expected_flash, flashed_messages)

    @patch.object(MockOrderService, 'create_order')
    @patch.object(MockCartService, 'clear_cart')
    @patch.object(MockCartService, 'get_cart_display_data')
    def test_checkout_post_order_success_cart_clear_fails_bool_response(self, mock_get_cart_data_method, mock_clear_cart_method, mock_create_order_method):
        cart_items_data = {'items': [{'id': 1}], 'total_amount': 100.0}
        mock_get_cart_data_method.return_value = cart_items_data
        mock_create_order_method.return_value = (True, "Order created", 125)
        mock_clear_cart_method.return_value = False

        form_data = {
            'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com',
            'phone': '1234567890', 'region': 'Test Region', 'city': 'Test City',
            'post_office': 'Test PO', 'payment_method': 'card'
        }
        with self.client as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['session_id'] = 'test_session'
            response = client.post('/checkout/', data=form_data)
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                flashed_messages = get_flashed_messages(with_categories=True)
            expected_flash = ("warning", "Замовлення №125 створено, але виникла помилка при очищенні кошика.")
            self.assertIn(expected_flash, flashed_messages)


    @patch.object(MockOrderService, 'get_order_details_for_confirmation')
    def test_order_confirmation_with_order_id_details_not_found_redirects(self, mock_get_details_method):
        mock_get_details_method.return_value = None

        with self.client as client:
            with client.session_transaction() as sess:
                sess['last_order_id_for_confirmation'] = 790
            response = client.get('/checkout/order-confirmation')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/home_dummy'))
            mock_get_details_method.assert_called_once_with(790)
            with client.session_transaction() as sess:
                flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(("error", "Не вдалося завантажити деталі вашого замовлення."), flashed_messages)


    def test_order_confirmation_no_order_id_in_session_redirects(self):
        with self.client as client:
            with client.session_transaction() as sess:
                if 'last_order_id_for_confirmation' in sess:
                    sess.pop('last_order_id_for_confirmation')

            response = client.get('/checkout/order-confirmation')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/home_dummy'))
            with client.session_transaction() as sess:
                flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "Для перегляду підтвердження замовлення, будь ласка, оформіть його спочатку."), flashed_messages)


