from django.contrib.auth.models import User
from django.contrib.auth import forms
from django.forms import fields
from django.test import Client
from django.test import TestCase
from django.urls import reverse


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create(username='Пользователь')
        cls.AUTHORIZED_CLIENT = Client()
        cls.AUTHORIZED_CLIENT.force_login(cls.USER)

    def test_page_user_signup(self):
        """Тест URL 'users:signup'"""
        response = UsersViewsTest.AUTHORIZED_CLIENT.get(
            reverse('users:signup')
        )
        test_dict = {
            'first_name': fields.CharField,
            'last_name': fields.CharField,
            'username': forms.UsernameField,
            'email': fields.EmailField,
        }
        for value, expected in test_dict.items():
            with self.subTest(value=value):
                response_value = response.context['form'].fields[value]
                self.assertIsInstance(response_value, expected)
