import shutil
import tempfile
from typing import Dict, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from faker import Faker
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
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.author.username,),
            ),
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

    def test_edit_post_acsses(self) -> None:
        """Проверка доступности редактирования поста для разных клиентов."""
        not_author = mixer.blend(User)
        post = mixer.blend('posts.Post', author=self.author)

        not_author_client = Client()
        not_author_client.force_login(user=not_author)
        new_form_data = {
            'text': Faker().bothify(),
        }
        self.assertRedirects(
            self.client.post(
                reverse('posts:post_edit', args=(post.pk,)),
                data=new_form_data,
                follow=True,
            ),
            redirect_to_login(
                next=reverse('posts:post_edit', args=(post.pk,)),
            ).url,
        )

        self.assertRedirects(
            not_author_client.post(
                reverse('posts:post_edit', args=(post.pk,)),
                data=new_form_data,
                follow=True,
            ),
            reverse('posts:post_detail', args=(post.pk,)),
        )
        self.assertEqual(
            post,
            self.author_client.get(
                reverse('posts:profile', args=(self.author.username,)),
            ).context['page_obj'][0],
        )


class TestCommentForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.post = mixer.blend('posts.Post')

        cls.auth = Client()
        cls.auth.force_login(user=cls.user)

    def test_comment_form(self) -> None:
        """Проверка работы формы добавления комментария и изменения в БД."""
        form_data = {
            'text': Faker().bothify(text='????'),
        }
        response = self.auth.post(
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
        comment = self.client.get(
            reverse(
                'posts:post_detail',
                args=(self.post.pk,),
            ),
        ).context['comments'][0]
        self.assertEqual(comment.text, form_data['text'])

        self.assertEqual(
            comment,
            Comment.objects.get(
                author=self.user,
                post=self.post.pk,
                text=form_data['text'],
            ),
        )
        self.assertEqual(Comment.objects.count(), 1)

    def test_comment_access(self) -> None:
        """Проверка доступности комментирования для разных клиентов."""
        form_data = {
            'text': Faker().bothify(),
        }
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
        self.assertEqual(Comment.objects.count(), 0)
