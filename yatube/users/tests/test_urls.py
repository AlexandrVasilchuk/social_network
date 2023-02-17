from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_available(self) -> None:
        """Провека доступности адресов."""
        response_values = [
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_change_form'),
            reverse('users:password_change_done'),
            reverse('users:password_reset_form'),
            reverse('users:password_reset_complete'),
            reverse('users:password_reset_done'),
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': 'MQ',
                    'token': '67t-0041e063fc003f28187f',
                },
            ),
            reverse('users:logout'),
        ]
        for response in response_values:
            with self.subTest(response=response):
                self.assertEqual(
                    self.authorized_client.get(response).status_code,
                    HTTPStatus.OK,
                    f'Страница {response} недоступна!',
                )

    def test_redirect_anonymous(self) -> None:
        """Проверка редиректа для анонимного пользователя."""
        response_values = {
            reverse('users:password_change_form'): redirect_to_login(
                next=reverse('users:password_change_form'),
            ).url,
            reverse('users:password_change_done'): redirect_to_login(
                next=reverse('users:password_change_done'),
            ).url,
        }
        for response, expected in response_values.items():
            with self.subTest(value=response):
                self.assertRedirects(
                    self.client.get(response),
                    expected,
                    msg_prefix=f'Страница {response} перенаправляет не туда!',
                )
