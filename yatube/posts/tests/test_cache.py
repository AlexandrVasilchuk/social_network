from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(TestCache.user)

    def test_index_cache(self) -> None:
        """Проверка доступности кеша index"""
        new_post = Post.objects.create(
            author=TestCache.user,
            text='1',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        response_content_1 = response.content
        new_post.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        response_content_2 = response_2.content
        self.assertEqual(response_content_1, response_content_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        response_content_3 = response_3.content
        self.assertNotEqual(response_content_2, response_content_3)
