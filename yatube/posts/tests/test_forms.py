import shutil
import tempfile
from typing import Dict, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post
from posts.tests.common import image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
UPLOADED_TO = Post.image.field.upload_to


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

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
            'author_id': self.user.pk,
            'pk': response.context['post'].pk,
            'image': UPLOADED_TO + data['image'].name,
        }
        for value, expected in value_expected.items():
            with self.subTest(value=expected):
                self.assertEqual(getattr(post, value), expected)

    def create_post(self) -> None:
        """Проверка добавления записи в БД при отправке валидной формы."""
        group = mixer.blend('posts.Group')
        form_data = {
            'text': 'Тестовый пост',
            'group': group.pk,
            'image': image(),
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        self.post_fields(response, form_data)

        self.assertRedirects(
            self.client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True,
            ),
            redirect_to_login(next=reverse('posts:post_create')).url,
        )

    def test_help_text_newpost_form(self) -> None:
        field_expected_value = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_expected_value.items():
            with self.subTest(value=expected_value):
                self.assertEqual(
                    self.authorized_client.get(reverse('posts:post_create'))
                    .context['form']
                    .fields[field]
                    .help_text,
                    expected_value,
                )

    def test_edit_post(self) -> None:
        """Проверка работы формы при изменении поста."""
        not_author = mixer.blend(User)
        not_author_client = Client()
        not_author_client.force_login(user=not_author)
        group = mixer.blend('posts.Group')
        post = mixer.blend('posts.Post', author=self.user)
        form_data = {
            'text': 'Изменённый текст',
            'group': group.pk,
            'image': image(),
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post.pk,)),
        )
        self.post_fields(response, form_data)
        self.assertRedirects(
            self.client.post(
                reverse('posts:post_edit', args=(post.pk,)),
                data=form_data,
                follow=True,
            ),
            redirect_to_login(
                next=reverse('posts:post_edit', args=(post.pk,)),
            ).url,
        )
        self.assertRedirects(
            not_author_client.post(
                reverse('posts:post_edit', args=(post.pk,)),
                data=form_data,
                follow=True,
            ),
            reverse('posts:post_detail', args=(post.pk,)),
        )


class TestCommentForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.post = mixer.blend('posts.Post', author=cls.user)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user=cls.user)

    def test_comment_form(self) -> None:
        """Проверка работы формы добавления комментария и изменения в БД."""
        form_data = {
            'text': 'Коммент Васи Пупкина',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.pk,),
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(self.post.pk,),
            ),
        )
        field_expected = {
            'author': self.user,
            'post_id': self.post.pk,
            'text': form_data['text'],
        }
        comment = self.client.get(
            reverse(
                'posts:post_detail',
                args=(self.post.pk,),
            ),
        ).context['comments'][0]
        for field, expected in field_expected.items():
            with self.subTest(value=field):
                self.assertEqual(getattr(comment, field), expected)

        self.assertEqual(
            comment,
            Comment.objects.get(
                author=self.user,
                post=self.post.pk,
                text=form_data['text'],
            ),
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertRedirects(
            self.client.post(
                reverse(
                    'posts:add_comment',
                    args=(self.post.pk,),
                ),
                data=form_data,
            ),
            redirect_to_login(
                next=reverse('posts:add_comment', args=(self.post.pk,)),
            ).url,
        )
