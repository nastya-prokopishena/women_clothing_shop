import unittest
from unittest.mock import patch, MagicMock
from app.application.services.user_page_service import (
    register_user, login_user, get_user_profile, update_user_name,
    update_user_surname, update_user_phone, change_user_password,
    request_password_reset, reset_password, add_user_address, delete_user_address
)
from app.domain.models import User


class TestUserPageService(unittest.TestCase):

    def setUp(self):
        # Створюємо патчери
        self.user_repo_patcher = patch('app.application.services.user_page_service.UserRepository')
        self.user_service_patcher = patch('app.application.services.user_page_service.user_service')
        self.send_reset_email = patch('app.application.services.user_page_service.send_reset_email')
        self.generate_serializer = patch('app.application.services.user_page_service.generate_serializer')
        self.hash_password = patch('app.application.services.user_page_service.user_service.hash_password')

        # Стартується патч і зберігається мок
        self.mock_user_repo = self.user_repo_patcher.start()
        self.mock_user_service = self.user_service_patcher.start()
        self.send_reset_email = self.send_reset_email.start()
        self.generate_serializer = self.generate_serializer.start()
        self.hash_password = self.hash_password.start()

        # Не забути додати зупинку патчів
        self.addCleanup(self.user_repo_patcher.stop)
        self.addCleanup(self.user_service_patcher.stop)
        self.addCleanup(self.send_reset_email.stop)
        self.addCleanup(self.generate_serializer.stop)
        self.addCleanup(self.hash_password.stop)

    # ----------- РЕЄСТРАЦІЯ -----------
    def test_register_user_success(self):
        """ Тестує успішну реєстрацію користувача, коли email ще не зареєстрований.
        Перевіряє виклик методів пошуку та вставки користувача."""
        repo = self.mock_user_repo.return_value
        repo.find_by_email.return_value = None
        repo.insert.return_value = True

        form = {'email': 'john@example.com', 'name': 'John', 'password': '1234'}
        success, msg = register_user(form)
        self.assertTrue(success)
        self.assertIn('успішна', msg)
        repo.find_by_email.assert_called_once_with('john@example.com')
        repo.insert.assert_called_once()

    def test_register_user_missing_fields(self):
        """Тестує спробу реєстрації користувача з пустими обовʼязковими полями.
        Очікує невдалий результат з повідомленням про необхідність заповнити поля."""
        form = {'email': '', 'name': '', 'password': ''}
        success, msg = register_user(form)
        self.assertFalse(success)
        self.assertIn('обовʼязковими', msg)

    def test_register_user_email_exists(self):
        """Тестує випадок реєстрації з email, який вже існує в базі.
        Очікує невдалий результат з відповідним повідомленням."""
        repo = self.mock_user_repo.return_value
        repo.find_by_email.return_value = MagicMock()

        form = {'email': 'exists@example.com', 'name': 'John', 'password': '1234'}
        success, msg = register_user(form)
        self.assertFalse(success)
        self.assertIn('вже існує', msg)

    # ----------- ЛОГІН -----------
    def test_login_user_success(self):
        """Тестує успішний вхід користувача з правильним email і паролем.
        Перевіряє, що повертається успіх і відповідні дані."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        user_mock.password_hash = 'hashedpassword'
        repo.find_by_email.return_value = user_mock

        with patch('app.application.services.user_page_service.user_service') as mock_service:
            mock_service.check_password.return_value = True
            form = {'email': 'john@example.com', 'password': '1234'}
            success, msg, data = login_user(form)
            self.assertTrue(success)
            self.assertIsNone(msg)
            self.assertIn('user_id', data)

    def test_login_user_wrong_password(self):
        """Тестує вхід користувача з неправильним паролем.
        Очікує невдалий результат з повідомленням про помилковий пароль."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        user_mock.password_hash = 'hashedpassword'
        repo.find_by_email.return_value = user_mock

        with patch('app.application.services.user_page_service.user_service') as mock_service:
            mock_service.check_password.return_value = False
            form = {'email': 'john@example.com', 'password': 'wrong'}
            success, msg, data = login_user(form)
            self.assertFalse(success)
            self.assertIn('Неправильна', msg)

    # ----------- ОТРИМАННЯ ПРОФІЛЮ ЗА ЕМЕЙЛОМ -----------
    def test_get_user_profile(self):
        """Тестує отримання профілю користувача за email.
        Перевіряє, що повернуті дані співпадають із введеними."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        user_mock.name = 'John'
        user_mock.surname = 'Doe'
        user_mock.email = 'john@example.com'
        user_mock.phone = '123456'
        user_mock.addresses = ['addr1', 'addr2']
        repo.find_by_email.return_value = user_mock

        profile = get_user_profile('john@example.com')
        self.assertEqual(profile['user_name'], 'John')
        self.assertEqual(profile['surname'], 'Doe')
        self.assertEqual(profile['user_email'], 'john@example.com')
        self.assertEqual(profile['user_phone'], '123456')
        self.assertEqual(profile['addresses'], ['addr1', 'addr2'])

    # ----------- ОНОВЛЕННЯ ІМЕНІ -----------
    def test_update_user_name_success(self):
        """Тестує успішне оновлення імені користувача.
        Перевіряє зміну значення та виклик оновлення в репозиторії."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        repo.find_by_email.return_value = user_mock

        form = {'name': 'NewName'}
        success, msg = update_user_name('john@example.com', form)
        self.assertTrue(success)
        self.assertIn('успішно', msg)
        self.assertEqual(user_mock.name, 'NewName')
        repo.update.assert_called_once_with(user_mock)

    def test_update_user_name_empty(self):
        """Тестує спробу оновлення імені з порожнім значенням.
        Очікує невдалий результат з повідомленням про відсутність введення."""
        form = {'name': ''}
        success, msg = update_user_name('john@example.com', form)
        self.assertFalse(success)
        self.assertIn('не введено', msg)

    # ----------- ОНОВЛЕННЯ ПРІЗВИЩА -----------
    def test_update_surname_success(self):
        """Тестує успішне оновлення прізвища користувача.
            Перевіряє, що значення змінюється, і що метод оновлення викликається."""
        mock_user = User(
            name="Test",
            email="test@example.com",
            password_hash="hashedpassword",
            surname="OldSurname"
        )
        mock_repo_instance = self.mock_user_repo.return_value
        mock_repo_instance.find_by_email.return_value = mock_user

        form = {"surname": "NewSurname"}
        success, message = update_user_surname("test@example.com", form)

        self.assertTrue(success)
        self.assertEqual(message, "Прізвище успішно додано.")
        self.assertEqual(mock_user.surname, "NewSurname")
        mock_repo_instance.update.assert_called_once_with(mock_user)

    def test_update_surname_empty(self):
        """Тестує спробу оновлення прізвища з порожнім значенням.
            Очікує невдалий результат з повідомленням про відсутність введення."""
        form = {"surname": " "}
        success, message = update_user_surname("test@example.com", form)

        self.assertFalse(success)
        self.assertEqual(message, "Прізвище не введено.")
        self.mock_user_repo.return_value.update.assert_not_called()

    # ----------- ОНОВЛЕННЯ НОМЕРА ТЕЛЕФОНА -----------
    def test_update_user_phone_success(self):
        """Тестує успішне оновлення номера телефона користувача.
        Перевіряє, що значення телефону змінюється, і викликається оновлення в репозиторії."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        repo.find_by_email.return_value = user_mock

        form = {'phone': '0987654321'}
        success, msg = update_user_phone('john@example.com', form)
        self.assertTrue(success)
        self.assertEqual(msg, "Номер телефону збережено.")
        self.assertEqual(user_mock.phone, '0987654321')
        repo.update.assert_called_once_with(user_mock)

    def test_update_user_phone_empty(self):
        """Тестує спробу оновлення телефону з порожнім значенням.
        Очікує невдалий результат з повідомленням про відсутність введення."""
        form = {'phone': '   '}
        success, msg = update_user_phone('john@example.com', form)
        self.assertFalse(success)
        self.assertEqual(msg, "Введіть номер телефону.")
        self.mock_user_repo.return_value.update.assert_not_called()

    # ----------- ЗМІНА ПАРОЛЯ -----------
    def test_change_user_password_success(self):
        """Тестує успішну зміну пароля користувача, коли введено правильний поточний пароль.
        Перевіряє, що пароль оновлюється і виконується оновлення у репозиторії."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        user_mock.password_hash = 'oldhash'
        repo.find_by_email.return_value = user_mock

        with patch('app.application.services.user_page_service.user_service') as mock_service:
            mock_service.check_password.return_value = True
            mock_service.hash_password.return_value = 'newhash'

            form = {'current_password': 'old', 'new_password': 'new'}
            success, msg = change_user_password('john@example.com', form)
            self.assertTrue(success)
            self.assertIn('успішно', msg)
            self.assertEqual(user_mock.password_hash, 'newhash')
            repo.update.assert_called_once_with(user_mock)

    def test_change_user_password_wrong_current(self):
        """Тестує спробу зміни пароля з неправильним поточним паролем.
        Очікує невдалий результат з відповідним повідомленням."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        repo.find_by_email.return_value = user_mock

        with patch('app.application.services.user_page_service.user_service') as mock_service:
            mock_service.check_password.return_value = False

            form = {'current_password': 'wrong', 'new_password': 'new'}
            success, msg = change_user_password('john@example.com', form)
            self.assertFalse(success)
            self.assertIn('Неправильний', msg)

    # ----------- ТЕСТУВАННЯ ВІДНОВЛЕННЯ ПАРОЛЯ -----------
    def test_request_password_reset_success(self):
        """Тест успішного створення токена для скидання пароля."""
        user_mock = MagicMock(email='john@example.com')
        self.mock_user_repo.return_value.find_by_email.return_value = user_mock

        serializer_mock = MagicMock()
        serializer_mock.dumps.return_value = 'fake-token'
        self.generate_serializer.return_value = serializer_mock

        success, msg = request_password_reset('john@example.com')

        self.assertTrue(success)
        self.assertEqual(msg, "Інструкції для скидання пароля надіслано на ваш email.")
        self.send_reset_email.assert_called_once_with(user_mock, 'fake-token')

    def test_request_password_reset_user_not_found(self):
        """Тест коли користувача не знайдено."""
        self.mock_user_repo.return_value.find_by_email.return_value = None
        success, msg = request_password_reset('unknown@example.com')
        self.assertFalse(success)
        self.assertEqual(msg, "Користувача з таким email не знайдено.")

    def test_reset_password_success(self):
        """Тест успішного скидання пароля через токен."""
        token = 'valid-token'
        email = 'john@example.com'
        form = {'new_password': 'newpass123'}
        serializer_mock = MagicMock()
        serializer_mock.loads.return_value = email
        self.generate_serializer.return_value = serializer_mock
        user_mock = MagicMock(email=email)
        self.mock_user_repo.return_value.find_by_email.return_value = user_mock
        self.hash_password.return_value = 'hashed_newpass'
        success, msg = reset_password(token, form)
        self.assertTrue(success)
        self.assertEqual(msg, "Пароль успішно змінено!")
        self.assertEqual(user_mock.password_hash, 'hashed_newpass')
        self.mock_user_repo.return_value.update.assert_called_once_with(user_mock)

    def test_reset_password_invalid_token(self):
        """Тест коли токен недійсний або протермінований."""
        serializer_mock = MagicMock()
        serializer_mock.loads.side_effect = Exception("Invalid token")
        self.generate_serializer.return_value = serializer_mock  # Виправлено self.self

        success, msg = reset_password('bad-token', {'new_password': '123'})
        self.assertFalse(success)
        self.assertIn("Недійсний або протермінований токен", msg)

    def test_reset_password_user_not_found(self):
        """Тест коли користувача за email з токена не знайдено."""
        serializer_mock = MagicMock()
        serializer_mock.loads.return_value = 'john@example.com'
        self.generate_serializer.return_value = serializer_mock

        self.mock_user_repo.return_value.find_by_email.return_value = None

        success, msg = reset_password('valid-token', {'new_password': '123'})
        self.assertFalse(success)
        self.assertEqual(msg, "Користувача не знайдено.")

    def test_reset_password_empty_password(self):
        """Тест коли новий пароль не введено."""
        serializer_mock = MagicMock()
        serializer_mock.loads.return_value = 'john@example.com'
        self.generate_serializer.return_value = serializer_mock

        self.mock_user_repo.return_value.find_by_email.return_value = MagicMock()

        success, msg = reset_password('valid-token', {'new_password': '   '})
        self.assertFalse(success)
        self.assertEqual(msg, "Введіть новий пароль.")

    # ----------- ВИДАЛЕННЯ АДРЕСИ -----------
    def test_delete_user_address(self):
        """Тестує видалення адреси користувача за id.
        Перевіряє, що адреса успішно видаляється з колекції і виконується оновлення."""
        repo = self.mock_user_repo.return_value
        addr1 = MagicMock(_id='id1')
        addr2 = MagicMock(_id='id2')
        user_mock = MagicMock()
        user_mock.addresses = [addr1, addr2]
        repo.find_by_email.return_value = user_mock

        success, msg = delete_user_address('john@example.com', 'id1')
        self.assertTrue(success)
        self.assertIn('видалено', msg)
        self.assertEqual(len(user_mock.addresses), 1)
        self.assertEqual(user_mock.addresses[0], addr2)
        repo.update.assert_called_once_with(user_mock)

    # ----------- ДОДАВАННЯ АДРЕСИ -----------
    def test_add_user_address_success(self):
        """Тестує успішне додавання адреси користувачу.
        Перевіряє, що створена адреса додається у колекцію адрес користувача і викликається оновлення."""
        repo = self.mock_user_repo.return_value
        user_mock = MagicMock()
        user_mock.addresses = []
        repo.find_by_email.return_value = user_mock

        # Налаштуємо mock для створення адреси
        new_address_mock = MagicMock()
        self.mock_user_service.create_address.return_value = new_address_mock

        form = {'city': 'Lviv', 'street': 'Zelena', 'house': '1', 'postal_code': '01001', 'country': 'Ukraine'}

        success, msg = add_user_address('john@example.com', form)

        self.assertTrue(success)
        self.assertIn('додано', msg)
        self.assertIn(new_address_mock, user_mock.addresses)
        repo.update.assert_called_once_with(user_mock)
        self.mock_user_service.create_address.assert_called_once_with(
            street='Zelena', city='Lviv', postal_code='01001', country='Ukraine', house='1'
        )


if __name__ == '__main__':
    unittest.main()
