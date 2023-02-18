from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import POST_SYMBOLS_LIMITATION, Comment, Follow, Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.post = mixer.blend('posts.Post')

    def test_verbose_name(self) -> None:
        """Verbose_name в полях совпадает с ожидаемым."""
        field_verbose = {
            'text': 'текст',
            'created': 'дата создания',
            'image': 'картинка',
            'group': 'группа',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_str_method(self) -> None:
        """Проверка метода __str__."""
        self.assertEqual(
            str(self.post),
            self.post.text[:POST_SYMBOLS_LIMITATION],
            'Метод __str__ работает неправильно для модели Post',
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = mixer.blend('posts.Group')

    def test_verbose_name(self) -> None:
        """Verbose_name в полях совпадает с ожидаемым."""
        field_verbose = {
            'title': 'заголовок',
            'description': 'описание',
            'slug': 'имя группы',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_str_method(self) -> None:
        """Проверка метода __str__."""
        self.assertEqual(
            str(self.group),
            self.group.title,
            'Метод __str__ работает неправильно для модели Group',
        )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.comment = mixer.blend('posts.Comment')

    def test_verbose_name(self) -> None:
        """Verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'текст',
            'created': 'дата создания',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Comment._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_str_method(self) -> None:
        """Проверка метода __str__."""
        self.assertEqual(
            str(self.comment),
            self.comment.text[:POST_SYMBOLS_LIMITATION],
            'Метод __str__ работает неправильно для модели Group',
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.follow = mixer.blend('posts.Follow')

    def test_verbose_name(self) -> None:
        """Verbose_name в полях совпадает с ожидаемым."""
        field_verbose = {
            'user': 'подписчик',
            'author': 'автор',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Follow._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_str_method(self) -> None:
        """Проверка метода __str__."""
        self.assertEqual(
            str(self.follow),
            f'Пользователь {self.follow.user.username} '
            f'подписан на автора {self.follow.author.username}',
            'Метод __str__ работает неправильно для модели Group',
        )
