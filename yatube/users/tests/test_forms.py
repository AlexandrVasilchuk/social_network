from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TestUsersForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_sign_in_form(self) -> None:
        """Проверка создания нового пользователя через форму."""
        form_data = {
            'first_name': 'Alexandr',
            'last_name': 'Vasilchuk',
            'username': 'vsko',
            'email': 'alexandrvsko@gmail.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        self.guest_client.post(reverse('users:signup'), data=form_data)
        self.assertEqual(
            User.objects.filter(username=form_data['username']).exists(),
            True,
        )
