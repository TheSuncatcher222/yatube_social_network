from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase

from http import HTTPStatus


class UsersURLTest(TestCase):
    """Тестирование URL приложения 'users'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER = User.objects.create(username='Пользователь')
        cls.GUEST_CLIENT = Client()
        cls.AUTHORIZED_CLIENT = Client()
        cls.test_dict_http = {
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/signup/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
        }
        cls.test_dict_html = {
            '/auth/login/': 'includes/users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/signup/': 'includes/users/signup.html',
            '/auth/logout/': 'includes/users/logged_out.html',
        }

    def setUp(self) -> None:
        self.AUTHORIZED_CLIENT.force_login(UsersURLTest.USER)

    def test_guest_pages_access_code(self) -> None:
        """Тест доступа неавторизованного пользователя к сайту"""
        test_dict_http = UsersURLTest.test_dict_http
        test_dict_http['/password_change/'] = HTTPStatus.NOT_FOUND
        for path, status in test_dict_http.items():
            response = UsersURLTest.GUEST_CLIENT.get(path, follow=True)
            with self.subTest(item=path):
                self.assertEqual(response.status_code, status)

    def test_authorized_client_pages_access_code(self) -> None:
        """Тест доступа авторизованного пользователя к сайту"""
        for path, status in UsersURLTest.test_dict_http.items():
            response = self.AUTHORIZED_CLIENT.get(path)
            with self.subTest(item=path):
                self.assertEqual(response.status_code, status)

    def test_guest_pages_access_template(self) -> None:
        """Тест шаблонов для неавторизованного пользователя"""
        test_dict_html = UsersURLTest.test_dict_html
        test_dict_html.pop('/auth/password_change/')
        for path, template in UsersURLTest.test_dict_html.items():
            response = self.AUTHORIZED_CLIENT.get(path)
            with self.subTest(item=path):
                self.assertTemplateUsed(response, template)

    def test_authorized_client_pages_access_template(self) -> None:
        """Тест шаблонов для авторизованного пользователя"""
        for path, template in UsersURLTest.test_dict_html.items():
            response = self.AUTHORIZED_CLIENT.get(path)
            with self.subTest(item=path):
                self.assertTemplateUsed(response, template)
