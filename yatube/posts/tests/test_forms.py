import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=TestPostForm.user,
            text='Пост # 1',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPostForm.user)

    def identification_post(self, response, form_data):
        """Проверка, что искомый пост = первый пост"""
        if 'page_obj' in response.context.keys():
            pk = response.context['page_obj'][0].pk
        else:
            pk = response.context['post'].pk
        self.assertEqual(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                author=TestPostForm.user.pk,
                pk=pk,
            ).exists(),
            True,
        )

    def test_newpost_form(self) -> None:
        """Проверка добавления записи в БД при отправке валидной формы"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        amount_posts = Post.objects.count()
        self.assertEqual(Post.objects.count(), amount_posts)
        form_data = {
            'text': 'Тестовый пост',
            'group': TestPostForm.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
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
        self.assertEqual(Post.objects.count(), amount_posts + 1)
        self.identification_post(response, form_data)

    def test_not_valid_form(self) -> None:
        """Проверка доступности страницы при отправке невалидной формы"""
        amount_posts = Post.objects.count()
        self.assertEqual(Post.objects.count(), amount_posts)
        form_data = {
            'text': '',
            'group': TestPostForm.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')
        self.assertEqual(Post.objects.filter(text='').exists(), False)
        self.assertEqual(Post.objects.count(), amount_posts)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self) -> None:
        """Проверка работы формы при изменении поста"""
        form_data = {
            'text': 'Измененный старый пост',
            'group': TestPostForm.group.pk,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': TestPostForm.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'pk': TestPostForm.post.pk}),
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

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(user=TestCommentForm.user)

    def test_comment_form(self) -> None:
        """Проверка работы формы добавления комментария и изменения в БД"""
        ammount_comments = Comment.objects.count()
        self.assertEqual(ammount_comments, 0)
        form_data = {
            'text': 'Коммент Васи Пупкина',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': TestCommentForm.post.pk,
                },
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'pk': TestCommentForm.post.pk,
                },
            ),
        )
        self.assertEqual(
            Comment.objects.filter(
                author=TestCommentForm.user,
                post=TestCommentForm.post.pk,
                text=form_data['text'],
            ).exists(),
            True,
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    'posts:post_detail',
                    kwargs={
                        'pk': TestCommentForm.post.pk,
                    },
                )
            ).context['comments'][0],
            Comment.objects.get(
                author=TestCommentForm.user,
                post=TestCommentForm.post.pk,
                text=form_data['text'],
            ),
        )
        self.assertEqual(Comment.objects.count(), ammount_comments + 1)
