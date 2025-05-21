from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.application.services.user_page_service import (register_user, login_user, get_user_profile, reset_password,
                                                        change_user_password, add_user_address, delete_user_address,
                                                        update_user_phone, request_password_reset, generate_serializer,
                                                        update_user_surname)


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        success, message = register_user(request.form)
        flash(message)
        if success:
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.register'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        success, message, session_data = login_user(request.form)
        if success:
            session.update(session_data)
            return redirect(url_for('auth.profile'))
        flash(message)
        return redirect(url_for('auth.login'))
    return render_template('login.html')


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('user_email')
    if not user_email:
        flash("Будь ласка, увійдіть у свій акаунт.")
        return redirect(url_for('auth.login'))

    user_data = get_user_profile(user_email)

    if request.method == 'POST':
        changes_made = False

        new_phone = request.form.get('phone')
        new_surname = request.form.get('surname')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if new_phone and new_phone != user_data["user_phone"]:
            update_user_phone(user_email, request.form)
            flash('Успішно змінено номер телефону', 'success')
            changes_made = True

        new_name = request.form.get('name')
        if new_name and new_name != user_data["user_name"]:
            from app.application.services.user_page_service import update_user_name
            update_user_name(user_email, request.form)
            flash('Успішно змінено імʼя', 'success')
            changes_made = True

        if new_surname and new_surname != user_data["surname"]:
            update_user_surname(user_email, request.form)
            flash('Успішно змінено прізвище', 'success')
            changes_made = True

        if current_password and new_password:
            success, message = change_user_password(user_email, request.form)
            flash(message, 'success' if success else 'error')
            changes_made = success or changes_made

        if request.form.get('save_address'):
            success, message = add_user_address(user_email, request.form)
            flash(message, 'success' if success else 'error')
            changes_made = True

        if request.form.get('delete_address_id'):
            address_id = request.form.get('delete_address_id')
            success, message = delete_user_address(user_email, address_id)
            flash(message, 'success' if success else 'error')
            changes_made = True

        if not changes_made:
            flash('Зміни не були внесені або не відрізняються від поточних', 'info')

        return redirect(url_for('auth.profile'))

    addresses = user_data.get("addresses", [])
    return render_template('profile.html', **user_data)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        success, message = request_password_reset(email)
        flash(message, 'success' if success else 'error')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_route(token):
    if request.method == 'POST':
        success, msg = reset_password(token, request.form)
        flash(msg, 'success' if success else 'error')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')
