from flask import Blueprint, render_template, request, redirect, url_for, session, flash # Додали flash
from app.application.services.cart_service import CartService # Імпортуємо ваш CartService

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout_bp.route('/', methods=['GET', 'POST']) # Змінено шлях на '/', бо є url_prefix
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
    fee = 0.00              # Приклад
    discount = 0.00         # Приклад
    total_order_amount = subtotal + delivery_price + fee - discount

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        region = request.form.get('region')
        city = request.form.get('city')
        post_office = request.form.get('post_office')
        payment_method = request.form.get('payment_method') # Змінено з 'payment' на 'payment_method'

        if not all([first_name, last_name, email, phone, region, city, post_office, payment_method]):
            flash("Будь ласка, заповніть усі обов'язкові поля.", "error")

            return render_template(
                'checkout.html',
                cart_items=current_cart_items,
                subtotal=subtotal,
                delivery_price=delivery_price,
                fee=fee,
                discount=discount,
                total_order_amount=total_order_amount,
                form_data=request.form
            )

        # Тут буде логіка створення замовлення в OrderService
        # order_service = OrderService()
        # success, order_message, created_order_id = order_service.create_order(
        #     user_id=user_id, # Або None, якщо гість
        #     customer_details={
        #         "first_name": first_name, "last_name": last_name,
        #         "email": email, "phone": phone
        #     },
        #     shipping_details={
        #         "region": region, "city": city, "post_office": post_office
        #     },
        #     payment_method=payment_method,
        #     cart_items=current_cart_items, # Передаємо актуальні товари з кошика
        #     subtotal=subtotal,
        #     delivery_price=delivery_price,
        #     total_amount=total_order_amount
        # )

        # if success:
        #     cart_service.clear_cart(user_id=user_id, session_id=session_id_val) # Очищення кошика
        #     session['order_id_for_confirmation'] = created_order_id # Зберігаємо ID для сторінки підтвердження
        #     flash("Замовлення успішно створено!", "success")
        #     return redirect(url_for('checkout.order_confirmation'))
        # else:
        #     flash(f"Помилка при створенні замовлення: {order_message}", "error")
        #     # Залишаємося на сторінці checkout, показуючи помилку

        # Тимчасове збереження даних у сесії для сторінки підтвердження (поки OrderService не реалізований)
        session['order_details'] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "region": region,
            "city": city,
            "address": post_office, # Використовуємо post_office як 'address' для сумісності з попереднім кодом
            "payment_method": payment_method,
            "total_price": total_order_amount, # Використовуємо розраховану загальну суму
            "items": current_cart_items # Зберігаємо деталі товарів
        }
        flash("Ваше замовлення отримано (тимчасово)! Дякуємо!", "success") # Тимчасове повідомлення
        return redirect(url_for('checkout.order_confirmation')) # Використовуємо ім'я Blueprint

    # Для GET запиту
    return render_template(
        'checkout.html',
        cart_items=current_cart_items, # Передаємо товари з кошика
        subtotal=subtotal,
        delivery_price=delivery_price,
        fee=fee,
        discount=discount,
        total_order_amount=total_order_amount, # Загальна сума до оплати
        form_data={} # Порожній словник для GET, щоб уникнути помилок у шаблоні
    )

@checkout_bp.route('/order-confirmation') # Залишаємо як частину checkout_bp
def order_confirmation():
    order_details = session.get('order_details', {})
    # Для реальної сторінки підтвердження краще отримувати дані замовлення з БД за order_id
    # order_id = session.pop('order_id_for_confirmation', None)
    # if order_id:
    #    order_service = OrderService()
    #    order = order_service.get_order_details_for_confirmation(order_id)
    #    return render_template('order_confirmation.html', order=order)
    # else:
    #    flash("Немає деталей для підтвердження замовлення.", "warning")
    #    return redirect(url_for('main.home'))

    return render_template('order_confirmation.html', order=order_details)

# Функція init_checkout_routes(app) більше не потрібна,
# оскільки ми використовуємо Blueprint, який реєструється в app/__init__.py.