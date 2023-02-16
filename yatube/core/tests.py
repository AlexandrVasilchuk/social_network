from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self) -> None:
        """Проверка недоступности страницы с кодом 404."""
        self.assertEqual(
            self.client.get('/nonexist-page/').status_code,
            HTTPStatus.NOT_FOUND,
        )

    def test_error_template(self) -> None:
        """Проверка использования верного шаблона."""
        self.assertTemplateUsed(
            self.client.get('/nonexists-page/'),
            'core/404.html',
        )
