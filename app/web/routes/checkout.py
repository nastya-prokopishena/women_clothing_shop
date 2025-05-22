# app/web/routes/checkout.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.application.services.cart_service import CartService
from app.application.services.order_service import OrderService

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')


@checkout_bp.route('/', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    session_id_val = session.get('session_id')

    cart_service = CartService()
    cart_data = cart_service.get_cart_display_data(user_id=user_id, session_id=session_id_val)

    if not cart_data or not cart_data.get('items'):
        flash("Ваш кошик порожній. Будь ласка, додайте товари перед оформленням.", "warning")
        return redirect(url_for('cart_bp.view_cart_page'))

    current_cart_items = cart_data.get('items', [])
    subtotal = cart_data.get('total_amount', 0.0)
    delivery_price = 50.00  # Приклад, поки що статичний
    fee = 0.00  # Приклад
    discount = 0.00  # Приклад
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

        order_service = OrderService()  # Створюємо екземпляр сервісу замовлень

        customer_details_from_form = {
            "first_name": first_name, "last_name": last_name,
            "email": email, "phone": phone
        }
        shipping_address_data = {
            "region": region, "city": city, "post_office": post_office
        }

        # Викликаємо метод створення замовлення БЕЗ customer_details
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
            # Очищення кошика після успішного створення замовлення
            clear_result = cart_service.clear_cart(user_id=user_id, session_id=session_id_val)

            # Обробка результату очищення кошика
            if isinstance(clear_result, tuple) and not clear_result[0]:
                flash(
                    f"Замовлення №{created_order_id} створено, але виникла помилка при очищенні кошика: {clear_result[1]}",
                    "warning")
            elif not clear_result and not isinstance(clear_result, tuple):  # Якщо повертає просто False
                flash(
                    f"Замовлення №{created_order_id} створено, але виникла помилка при очищенні кошика.",
                    "warning")
            else:  # Успішне очищення або clear_cart не повертає деталі помилки для відображення
                flash(f"Замовлення №{created_order_id} успішно створено! {order_message}", "success")

            session['last_order_id_for_confirmation'] = created_order_id  # Зберігаємо ID для сторінки підтвердження
            session.pop('order_details', None)  # Видаляємо старі тимчасові деталі, якщо вони були
            return redirect(url_for('auth.profile') + '?tab=orders')
        else:
            # Якщо створення замовлення не вдалося (наприклад, товару немає на складі)
            flash(f"Помилка при створенні замовлення: {order_message}", "error")
            # Залишаємося на сторінці checkout, показуючи помилку і зберігаючи дані форми
            return render_template('checkout.html', cart_items=current_cart_items, subtotal=subtotal,
                                   delivery_price=delivery_price, fee=fee, discount=discount,
                                   total_order_amount=total_order_amount, form_data=form_data)
        # --------------------------------------------------------------------

    # Для GET запиту
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
def order_confirmation():
    order_id = session.pop('last_order_id_for_confirmation', None)

    if order_id:
        order_service = OrderService()
        # Метод get_order_details_for_confirmation має бути реалізований в OrderService
        # і повертати дані, зрозумілі для шаблону order_confirmation.html
        order_data_for_template = order_service.get_order_details_for_confirmation(order_id)
        if order_data_for_template:
            return render_template('order_confirmation.html', order=order_data_for_template)
        else:
            flash("Не вдалося завантажити деталі вашого замовлення.", "error")
            return redirect(url_for('main.home'))  # Або інший відповідний маршрут
    else:
        flash("Для перегляду підтвердження замовлення, будь ласка, оформіть його спочатку.", "info")
        return redirect(url_for('main.home'))