# app/web/routes/cart.py
from flask import Blueprint, render_template, session, request, redirect, url_for, flash
# Переконайтеся, що шлях до вашого CartService правильний
from app.application.services.cart_service import CartService
import uuid  # Для генерації унікальних session_id для гостей

# Створюємо Blueprint для маршрутів кошика
cart_bp = Blueprint('cart_bp', __name__, url_prefix='/cart')


@cart_bp.route('/')
def view_cart_page():
    """
    Відображає сторінку кошика з поточними товарами.
    """
    user_id = session.get('user_id')
    session_id_val = session.get('session_id')  # Використовуємо інше ім'я, щоб не конфліктувати з flask.session

    cart_service = CartService()
    # Отримуємо дані кошика для відображення (список товарів та загальну суму)
    cart_data = cart_service.get_cart_display_data(user_id=user_id, session_id=session_id_val)

    return render_template(
        'cart.html',
        cart_items=cart_data.get('items', []),
        cart_total=cart_data.get('total_amount', 0.0)
    )


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """
    Обробляє додавання товару до кошика.
    Очікує POST-запит з даними товару з форми на сторінці товару.
    """
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        # Отримуємо кількість, за замовчуванням 1, і конвертуємо в ціле число
        quantity = request.form.get('quantity', 1, type=int)
        color = request.form.get('color')  # Обраний колір з форми
        size = request.form.get('size')  # Обраний розмір з форми

        if not product_id:
            flash('Не вдалося додати товар: ID товару відсутній.', 'error')
            # Повертаємо користувача на попередню сторінку або на головну
            return redirect(request.referrer or url_for('main.home'))  # 'main.home' - приклад

        if quantity < 1:
            quantity = 1  # Мінімальна кількість - 1

        user_id = session.get('user_id')
        session_id_val = session.get('session_id')

        # Якщо користувач не залогінений і немає session_id, генеруємо новий
        if not user_id and not session_id_val:
            session_id_val = str(uuid.uuid4())
            session['session_id'] = session_id_val  # Зберігаємо новий session_id в сесію Flask

        cart_service = CartService()
        # Метод сервісу повертає кортеж (success: bool, message: str)
        success, message = cart_service.add_product_to_cart(
            user_id=user_id,
            session_id=session_id_val,
            product_id=product_id,
            quantity=quantity,
            color=color,
            size=size
        )

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

        # Редирект на сторінку кошика, щоб користувач побачив оновлення
        return redirect(url_for('cart_bp.view_cart_page'))

    # Якщо запит не POST (малоймовірно, якщо форма налаштована правильно)
    return redirect(url_for('main.home'))  # Замініть на ваш головний маршрут


@cart_bp.route('/remove', methods=['POST'])
def remove_from_cart():
    """
    Обробляє видалення товару з кошика.
    Очікує POST-запит з даними товару, який потрібно видалити.
    """
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        # Отримуємо size та color, якщо вони використовуються для ідентифікації CartItem
        size = request.form.get('size')
        color = request.form.get('color')

        if not product_id:
            flash('Не вдалося видалити товар: ID товару відсутній.', 'error')
            return redirect(url_for('cart_bp.view_cart_page'))

        user_id = session.get('user_id')
        session_id_val = session.get('session_id')

        cart_service = CartService()
        success, message = cart_service.remove_product_from_cart(
            user_id=user_id,
            session_id=session_id_val,
            product_id=product_id,
            size=size,
            color=color
        )

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

        return redirect(url_for('cart_bp.view_cart_page'))

    return redirect(url_for('cart_bp.view_cart_page'))


@cart_bp.route('/update', methods=['POST'])
def update_cart_item():  # Поки що це заглушка, назва може бути іншою
    """
    Обробляє оновлення кількості товару в кошику.
    (Цей маршрут ще не реалізований повністю в наших обговореннях)
    """
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity', type=int)
        size = request.form.get('size')  # Якщо потрібно для ідентифікації
        color = request.form.get('color')  # Якщо потрібно для ідентифікації

        # Тут буде логіка виклику CartService для оновлення кількості
        # cart_service = CartService()
        # success, message = cart_service.update_cart_item_quantity(...)

        # flash(message, 'success' if success else 'error')
        flash(f'Тимчасово: Оновлення товару {product_id} до кількості {quantity} (ще не реалізовано)', 'info')

        return redirect(url_for('cart_bp.view_cart_page'))
    return redirect(url_for('cart_bp.view_cart_page'))