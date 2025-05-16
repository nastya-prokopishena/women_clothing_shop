from app.domain.services.email_service import send_reset_email
from app.infrastructure.persistence.user_repository import UserRepository
from app.domain.services.user_service import UserService
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

user_service = UserService()


def register_user(form):
    repo = UserRepository()
    email = form.get('email')
    name = form.get('name')
    password = form.get('password')
    if not email or not name or not password:
        return False, 'Усі поля є обовʼязковими.'
    if repo.find_by_email(email):
        return False, 'Користувач з таким email вже існує.'
    password_hash = user_service.hash_password(password)
    user = user_service.create_user(name=name, email=email, password_hash=password_hash)
    repo.insert(user)
    return True, 'Реєстрація успішна! Увійдіть до свого акаунту.'


def login_user(form):
    repo = UserRepository()
    email = form.get('email')
    password = form.get('password')
    user = repo.find_by_email(email)
    if not user or not user_service.check_password(password, user.password_hash):
        return False, 'Неправильна пошта або пароль.', {}
    return True,  None, {'user_id': str(user._id), 'user_name': user.name,
                                                    'user_email': user.email}


def get_user_profile(email):
    repo = UserRepository()
    user = repo.find_by_email(email)
    return {'user_name': user.name, 'surname': user.surname, 'user_email': user.email, 'user_phone': user.phone,
            'addresses': user.addresses}


def update_user_name(email, form):
    repo = UserRepository()
    name = form.get("name", "").strip()
    if not name:
        return False, "Імʼя не введено."
    user = repo.find_by_email(email)
    user.name = name
    repo.update(user)
    return True, "Імʼя успішно оновлено."


def update_user_surname(email, form):
    repo = UserRepository()
    surname = form.get("surname", "").strip()
    if not surname:
        return False, "Прізвище не введено."
    user = repo.find_by_email(email)
    user.surname = surname
    repo.update(user)
    return True, "Прізвище успішно додано."


def update_user_phone(email, form):
    repo = UserRepository()
    phone = form.get("phone", "").strip()
    if not phone:
        return False, "Введіть номер телефону."
    user = repo.find_by_email(email)
    user.phone = phone
    repo.update(user)
    return True, "Номер телефону збережено."


def change_user_password(email, form):
    repo = UserRepository()
    current_password = form.get('current_password', '').strip()
    new_password = form.get('new_password', '').strip()
    if not current_password or not new_password:
        return False, 'Будь ласка, заповніть обидва поля пароля.'
    user = repo.find_by_email(email)
    if not user:
        return False, 'Користувача не знайдено.'
    if not user_service.check_password(current_password, user.password_hash):
        return False, 'Неправильний поточний пароль.'
    user.password_hash = user_service.hash_password(new_password)
    repo.update(user)
    return True, 'Ваш пароль успішно змінено.'


def generate_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def request_password_reset(email):
    repo = UserRepository()
    user = repo.find_by_email(email)
    if not user:
        return False, "Користувача з таким email не знайдено."
    serializer = generate_serializer()
    token = serializer.dumps(user.email, salt='password-reset-salt')
    send_reset_email(user, token)
    return True, "Інструкції для скидання пароля надіслано на ваш email."


def reset_password(token, form):
    repo = UserRepository()
    serializer = generate_serializer()
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        return False, "Недійсний або протермінований токен."
    user = repo.find_by_email(email)
    if not user:
        return False, "Користувача не знайдено."
    new_password = form.get("new_password", "").strip()
    if not new_password:
        return False, "Введіть новий пароль."
    user.password_hash = user_service.hash_password(new_password)
    repo.update(user)
    return True, "Пароль успішно змінено!"


def add_user_address(email, form):
    repo = UserRepository()
    city = form.get('city', '').strip()
    street = form.get('street', '').strip()
    house = form.get('house', '').strip()
    postal_code = form.get('postal_code', '').strip()
    country = form.get('country', '').strip()
    if not city or not street or not house or not postal_code or not country:
        return False, 'Будь ласка, заповніть усі поля адреси.'
    user = repo.find_by_email(email)
    new_address = user_service.create_address(street=street, city=city, postal_code=postal_code, country=country,
                                              house=house)
    user.addresses.append(new_address)
    repo.update(user)
    return True, 'Адресу додано.'


def delete_user_address(email, address_id):
    repo = UserRepository()
    user = repo.find_by_email(email)
    user.addresses = [a for a in user.addresses if str(getattr(a, '_id', '')) != address_id]
    repo.update(user)
    return True, 'Адресу видалено.'
