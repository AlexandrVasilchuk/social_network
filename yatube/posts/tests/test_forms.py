import shutil
import tempfile
from typing import Dict, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post
from posts.tests.common import image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='vsko')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(TestPostForm.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def identification_post(
        self,
        response: HttpResponse,
        form_data: Dict['str', Union[Post, Group, int, str]],
    ) -> None:
        """Проверка, что искомый пост = первый пост."""
        post = Post.objects.get(pk=response.context['post'].pk)
        value_expected = {
            post.group.pk: form_data['group'],
            post.text: form_data['text'],
            post.author.pk: self.user.pk,
            post.pk: response.context['post'].pk,
        }
        for value, expected in value_expected.items():
            with self.subTest(value=expected):
                self.assertEqual(value, expected)

    def test_newpost_form(self) -> None:
        """Проверка добавления записи в БД при отправке валидной формы."""
        group = mixer.blend('posts.Group')
        self.assertEqual(Post.objects.count(), 0)
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
                kwargs={'username': TestPostForm.user.username},
            ),
        )
        self.assertEqual(
            response.context['page_obj'][0].image.name,
            Post.image.field.upload_to + form_data['image'].name,
        )
        self.assertEqual(Post.objects.count(), 1)
        self.identification_post(response, form_data)

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
        new_group = mixer.blend('posts.Group')
        post = mixer.blend('posts.Post', author=self.user)
        form_data = {
            'text': 'Изменённый текст',
            'group': new_group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'pk': post.pk}),
        )
        self.identification_post(response, form_data)


class TestCommentForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='vsko',
        )
        cls.post = Post.objects.create(
            author=TestCommentForm.user,
            text='Тестовый пост',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user=TestCommentForm.user)

    def test_comment_form(self) -> None:
        """Проверка работы формы добавления комментария и изменения в БД."""
        self.assertEqual(Comment.objects.count(), 0)
        form_data = {
            'text': 'Коммент Васи Пупкина',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'pk': self.post.pk,
                },
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'pk': self.post.pk,
                },
            ),
        )
        self.assertEqual(
            Comment.objects.filter(
                author=self.user,
                post=self.post.pk,
                text=form_data['text'],
            ).exists(),
            True,
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    'posts:post_detail',
                    kwargs={
                        'pk': self.post.pk,
                    },
                ),
            ).context['comments'][0],
            Comment.objects.get(
                author=self.user,
                post=self.post.pk,
                text=form_data['text'],
            ),
        )
        self.assertEqual(Comment.objects.count(), 1)
