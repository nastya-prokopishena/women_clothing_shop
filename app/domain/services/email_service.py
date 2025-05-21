from flask_mail import Message
from flask import url_for
from app.extensions import mail


def send_reset_email(user, token):
    reset_url = url_for('auth.reset_password_route', token=token, _external=True)
    msg = Message('Скидання пароля', recipients=[user.email])
    msg.body = f'Щоб скинути пароль, перейдіть за посиланням: {reset_url}'

    print(f"📤 Надсилаємо листа на {user.email} з посиланням: {reset_url}")

    mail.send(msg)
