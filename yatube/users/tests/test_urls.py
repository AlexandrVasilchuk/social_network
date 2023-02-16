from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersURLTest.user)

    def test_urls_available(self) -> None:
        """Провека доступности адресов."""
        response_values = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password/change/form/',
            '/auth/password/change/done/',
            '/auth/password/reset/form/',
            '/auth/password/reset/complete/',
            '/auth/password/reset/done/',
            '/auth/password/reset/MQ/67t-0041e063fc003f28187f/',
            '/auth/logout/',
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
            '/auth/password/change/form/': '/auth/login/?next=%2Fauth%2F'
            'password%2Fchange%2Fform%2F',
            '/auth/password/change/done/': '/auth/login/?next=%2Fauth%2F'
            'password%2Fchange%2Fdone%2F',
        }
        for response, expected in response_values.items():
            with self.subTest(value=response):
                self.assertRedirects(
                    self.client.get(response),
                    expected,
                    msg_prefix=f'Страница {response} перенаправляет не туда!',
                )
