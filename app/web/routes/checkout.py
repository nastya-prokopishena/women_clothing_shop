from flask import render_template, request, redirect, url_for, session


def init_checkout_routes(app):
    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        # Тимчасові статичні дані про товари (для прикладу)
        cart_items = [
            {"id": "1", "name": "Сукня Весна", "price": 1500, "quantity": 1},
            {"id": "2", "name": "Сукня Літо", "price": 1700, "quantity": 1}
        ]
        total_price = sum(item["price"] * item["quantity"] for item in cart_items)

        if request.method == 'POST':
            # Отримання даних з форми
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            city = request.form.get('city')
            address = request.form.get('address')
            payment_method = request.form.get('payment')

            # Тимчасове збереження даних у сесії (для прикладу)
            session['order_details'] = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "city": city,
                "address": address,
                "payment_method": payment_method,
                "total_price": total_price
            }

            # Перенаправлення на сторінку підтвердження
            return redirect(url_for('order_confirmation'))

        return render_template(
            'checkout.html',
            cart_items=cart_items,
            total_price=total_price
        )

    @app.route('/order-confirmation')
    def order_confirmation():
        order_details = session.get('order_details', {})
        return render_template('order_confirmation.html', order=order_details)