from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticPagesTest(TestCase):
    def test_about_urls(self) -> None:
        """Проверка доступности страниц приложения about."""
        response_values = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for value, expected in response_values.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.client.get(value).status_code,
                    expected,
                    f'Страница {value} недоступна по нужному адресу!',
                )


class StaticPagesViewsTest(TestCase):
    def test_about_views(self) -> None:
        """Проверка использования верных шаблонов."""
        response_values = {
            'about:author': 'about/about.html',
            'about:tech': 'about/tech.html',
        }
        for response, expected in response_values.items():
            with self.subTest(expected=expected):
                self.assertTemplateUsed(
                    self.client.get(reverse(response)),
                    expected,
                )
