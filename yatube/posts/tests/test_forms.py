import shutil
import tempfile
from typing import Dict, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer

from posts.models import Comment, Follow, Group, Post
from posts.tests.common import image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = mixer.blend(User)

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def post_fields(
        self,
        response: HttpResponse,
        data: Dict['str', Union[Post, Group, int, str]],
    ) -> None:
        """Проверка, что искомый пост = первый пост.

        Args:
            data: Словарь с данными, отправленными в форму
                создания/изменения поста.
            response: Страница, на которой отображается
                опубликованный/изменённый пост.
        """
        post = response.context['post']
        value_expected = {
            'group_id': data['group'],
            'text': data['text'],
            'author_id': self.author.pk,
            'pk': response.context['post'].pk,
        }
        self.assertTrue(
            response.context['post'].image.name.endswith(data['image'].name),
        )
        for value, expected in value_expected.items():
            with self.subTest(value=expected):
                self.assertEqual(getattr(post, value), expected)

    def create_post(self) -> None:
        """Проверка добавления записи в БД при отправке валидной формы."""
        group = mixer.blend('posts.Group')
        data = {
            'text': Faker().bothify(),
            'group': group.pk,
            'image': image(),
        }
        response = self.auth.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        self.post_fields(response, data)

    def test_create_accses(self) -> None:
        """Проверка доступа к созданию поста у анонимного пользователя."""
        form_data = {
            'text': Faker().bothify(),
        }
        self.client.post(reverse('posts:post_create'), form_data=form_data)
        self.assertEqual(Post.objects.count(), 0)

    def test_help_text_newpost_form(self) -> None:
        field_expected_value = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_expected_value.items():
            with self.subTest(value=expected_value):
                self.assertEqual(
                    self.author_client.get(reverse('posts:post_create'))
                    .context['form']
                    .fields[field]
                    .help_text,
                    expected_value,
                )

    def test_edit_post(self) -> None:
        """Проверка работы формы при изменении поста."""
        group = mixer.blend('posts.Group')
        post = mixer.blend('posts.Post', author=self.author)
        form_data = {
            'text': Faker().bothify(),
            'group': group.pk,
            'image': image(),
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post.pk,)),
        )
        self.post_fields(response, form_data)

    def test_edit_post_not_author(self) -> None:
        """Проверка редактирования поста для не автора."""
        not_author, not_author_client = mixer.blend(User), Client()
        post = mixer.blend('posts.Post', author=self.author)

        not_author_client.force_login(user=not_author)
        new_form_data = {
            'text': Faker().bothify(),
        }
        not_author_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=new_form_data,
            follow=True,
        )
        self.assertNotEqual(
            post.text,
            new_form_data['text'],
        )

    def test_edit_post_anonymous(self) -> None:
        """Проверка редактирования поста для анонимного пользователя."""
        post = mixer.blend('posts.Post', author=self.author)

        new_form_data = {
            'text': Faker().bothify(),
        }
        self.client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=new_form_data,
            follow=True,
        )
        self.assertNotEqual(
            post.text,
            new_form_data['text'],
        )


class TestCommentForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = mixer.blend(User)
        cls.post = mixer.blend('posts.Post')

        cls.author_client = Client()
        cls.author_client.force_login(user=cls.author)

    def comment_fields(
        self,
        data: Dict['str', str],
    ) -> None:
        """Проверка, что искомый комментарий = первый комментарий.

        Args:
            data: Словарь с данными, отправленными в форму
                создания комментария.
            response: Страница, на которой отображается
                опубликованный/изменённый пост.
        """
        comment = self.client.get(
            reverse('posts:post_detail', args=(self.post.pk,)),
        ).context['comments'][0]
        value_expected = {
            'text': data['text'],
            'author_id': self.author.pk,
            'post_id': self.post.pk,
        }
        for value, expected in value_expected.items():
            with self.subTest(value=expected):
                self.assertEqual(getattr(comment, value), expected)

    def test_comment_form(self) -> None:
        """Проверка работы формы добавления комментария и изменения в БД."""
        form_data = {
            'text': Faker().bothify(text='????'),
        }
        self.author_client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.pk,),
            ),
            data=form_data,
        )
        self.comment_fields(form_data)
        self.assertEqual(Comment.objects.count(), 1)

    def test_comment_anonymous(self) -> None:
        """Проверка доступности комментирования для анонимного пользователя."""
        form_data = {
            'text': Faker().bothify(text='????'),
        }
        self.client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.pk,),
            ),
            data=form_data,
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_self_comment(self) -> None:
        """Проверка комментирования под собственным постом."""
        form_data = {
            'text': Faker().bothify(text='????'),
        }
        self.author_client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.pk,),
            ),
            data=form_data,
        )
        self.comment_fields(form_data)


class FollowTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.follower, cls.author = mixer.blend(User), mixer.blend(User)

        cls.follow_client, cls.author_client = Client(), Client()
        cls.follow_client.force_login(user=cls.follower)
        cls.author_client.force_login(user=cls.author)

    def test_follow(self) -> None:
        """Проверка подписки и отписки для обычного пользователя."""
        self.follow_client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertTrue(
            Follow.objects.filter(
                author__following__user=self.follower,
                author=self.author,
            ).exists(),
        )
        self.assertEqual(
            Follow.objects.filter(
                author__following__user=self.follower,
                author=self.author,
            ).count(),
            1,
        )

        self.follow_client.get(
            reverse('posts:profile_unfollow', args=(self.author.username,)),
        )
        self.assertFalse(
            Follow.objects.filter(
                author__following__user=self.follower,
                author=self.author,
            ).exists(),
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_self_follow(self) -> None:
        """Проверка возможности самоподписки."""
        self.author_client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_anonymous_follow(self) -> None:
        """Проверка возможности подписки ананимом."""
        self.client.get(
            reverse('posts:profile_follow', args=(self.author.username,)),
        )
        self.assertEqual(Follow.objects.count(), 0)
