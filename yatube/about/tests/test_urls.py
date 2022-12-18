from django.test import Client
from django.test import TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    """Тестирование URL приложения 'about'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.GUEST_CLIENT = Client()

    def test_pages_access_code_template(self) -> None:
        """Тест доступа к сайту"""
        test_dict_http = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for value, expected in test_dict_http.items():
            with self.subTest(value=value):
                response = StaticURLTests.GUEST_CLIENT.get(value)
                self.assertEqual(response.status_code, expected)

    def test_pages_access_template(self) -> None:
        """Тест шаблонов"""
        test_dict_html = {
            '/about/author/': 'includes/about/about_author.html',
            '/about/tech/': 'includes/about/about_tech.html',
        }
        for value, expected in test_dict_html.items():
            with self.subTest(value=value):
                response = StaticURLTests.GUEST_CLIENT.get(value)
                self.assertTemplateUsed(response, expected)
