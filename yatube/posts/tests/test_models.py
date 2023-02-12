from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import POST_SYMBOLS_LIMITATION, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostModelTest.user,
            text='Тестовый пост более 15 символов',
        )

    def test_help_text(self) -> None:
        """Проверка help_text в полях совпадает с ожидаемым."""
        task = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).help_text, expected
                )

    def test_str_method(self) -> None:
        """Проверка метода __str__"""
        group = PostModelTest.group
        post = PostModelTest.post
        field_title = {
            str(group): PostModelTest.group.title,
            str(post): PostModelTest.post.text[:POST_SYMBOLS_LIMITATION],
        }
        for value, expected in field_title.items():
            with self.subTest(value=value):
                self.assertEqual(
                    expected, value, 'Метод __str__ работает неправильно!'
                )
