from http import HTTPStatus
from django.urls import reverse
from django.test import TestCase, Client


class ViewTestClass(TestCase):

    def setUp(self) -> None:
        self.csrf_user = Client(enforce_csrf_checks=True)

    def test_error_page(self):
        """Проверка недоступности страницы с кодом 404"""
        self.assertEqual(
            self.client.get('/nonexist-page/').status_code,
            HTTPStatus.NOT_FOUND,
        )
        self.assertEqual(self.csrf_user.get(reverse('posts:index')).status_code, HTTPStatus.FORBIDDEN)

    def test_error_template(self):
        """Проверка использования верного шаблона"""
        self.assertTemplateUsed(
            self.client.get('/nonexists-page/'),
            'core/404.html',
        )
