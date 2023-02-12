from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostURLTest.user,
            group=PostURLTest.group,
            text='Тестовый пост более 15 символов',
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user)
        cache.clear()

    def test_pages_available(self) -> None:
        """Проверка доступности страниц по указанным адресам для всех"""
        response_values = {
            self.client.get(''): HTTPStatus.OK,
            self.client.get(
                f'/group/{PostURLTest.group.slug}/'
            ): HTTPStatus.OK,
            self.client.get(
                f'/profile/{PostURLTest.user.username}/'
            ): HTTPStatus.OK,
            self.client.get(f'/posts/{PostURLTest.post.pk}/'): HTTPStatus.OK,
        }
        for value, expected in response_values.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value.status_code,
                    expected,
                    f'Страница {value} не доступна всем по нужному адресу!',
                )

    def test_redirect_for_anonymous(self) -> None:
        """Проверка редиректа анонимного пользователя"""
        response_values = {
            self.client.get(
                '/create/', follow=True
            ): '/auth/login/?next=/create/',
            self.client.get(
                f'/posts/{PostURLTest.post.pk}/edit/', follow=True
            ): f'/auth/login/?next=/posts/{PostURLTest.post.pk}/edit/',
            self.client.get(
                f'/posts/{PostURLTest.post.pk}/comment/', follow=True
            ): f'/auth/login/?next=/posts/{PostURLTest.post.pk}/comment/',
            self.client.get(
                '/follow/', follow=True
            ): '/auth/login/?next=/follow/',
        }
        for value, expected in response_values.items():
            with self.subTest(value=value):
                self.assertRedirects(
                    value,
                    expected,
                    msg_prefix=f'Редирект для {expected} не работает!',
                )

    def test_available_allowed_pages(self) -> None:
        """Проверка доступности страницы для авторизованного"""
        response_values = {
            self.authorized_client.get('/create/'): HTTPStatus.OK,
            self.authorized_client.get('/follow/'): HTTPStatus.OK,
        }
        for value, expected in response_values.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value.status_code,
                    expected,
                    'Страницы недоступны авторизованным пользователям!',
                )

    def test_author_available(self) -> None:
        """Проверка достуности страницы для автора поста"""
        self.assertEqual(
            self.authorized_client.get(
                f'/posts/{PostURLTest.post.pk}/edit/'
            ).status_code,
            HTTPStatus.OK,
        )

    def test_redirect_not_author(self) -> None:
        """Проверка редиректа гостя при попытке изменить пост"""
        self.not_author = User.objects.create_user(username='_')
        self.authorized_client.force_login(self.not_author)
        response = self.authorized_client.get(
            f'/posts/{PostURLTest.post.pk}/edit/'
        )
        value = f'/posts/{PostURLTest.post.pk}/'
        self.assertRedirects(response, value)

    def test_template_available(self) -> None:
        """Проверка обращение по url использует верный шаблон"""
        response_values = {
            '': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/group/{PostURLTest.group.slug}/': 'posts/group_list.html',
            f'/posts/{PostURLTest.post.pk}/': 'posts/post_detail.html',
            f'/posts/{PostURLTest.post.pk}/edit/': 'posts/create_post.html',
            f'/profile/{PostURLTest.user.username}/': 'posts/profile.html',
            '/follow/': 'posts/follow.html',
        }
        for response, value in response_values.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    self.authorized_client.get(response),
                    value,
                    f'Открывается неверный шаблон по ссылке {response}!',
                )
