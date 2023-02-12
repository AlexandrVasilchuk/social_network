import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestViewsPosts(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=TestViewsPosts.user,
            group=TestViewsPosts.group,
            text='Тестовый пост более 15 символов',
            image=uploaded,
        )
        cls.extra_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug_extra',
            description='Тестовое описание',
        )
        cls.follower_user = User.objects.create_user(username='vsko')

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(TestViewsPosts.user)
        self.follower_user_client = Client()
        self.follower_user_client.force_login(TestViewsPosts.follower_user)
        cache.clear()

    def test_correct_templates(self) -> None:
        """Обращение по namespace:name возвращают правильный шаблон"""
        response_expected = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_list', kwargs={'slug': TestViewsPosts.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail', kwargs={'pk': TestViewsPosts.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'pk': TestViewsPosts.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:profile',
                kwargs={'username': TestViewsPosts.user.username},
            ): 'posts/profile.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for response, value in response_expected.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    self.authorized_client.get(response),
                    value,
                    msg_prefix=f'Вызывается не тот шаблон {value}!',
                )

    def correct_page_obj_first_obj(self, context) -> None:
        """Проверка соотвествия поста на странице"""
        fields_to_check = {
            context.pk: TestViewsPosts.post.pk,
            context.author.username: TestViewsPosts.user.username,
            context.group.title: TestViewsPosts.group.title,
            context.text: TestViewsPosts.post.text,
            context.image: TestViewsPosts.post.image,
        }
        for field, expected in fields_to_check.items():
            with self.subTest(expected=expected):
                self.assertEqual(field, expected)

    def test_index_context(self) -> None:
        """Шаблон index сформирован с правильным контекстом."""
        first_object = self.authorized_client.get(
            reverse('posts:index')
        ).context['page_obj'][0]

        self.correct_page_obj_first_obj(first_object)

    def test_group_list_context(self) -> None:
        """Проверка правильности контекста для group_list"""
        first_object = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': TestViewsPosts.group.slug}
            )
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(first_object)
        self.assertEqual(
            self.authorized_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': TestViewsPosts.group.slug},
                )
            ).context['group'],
            TestViewsPosts.group,
        )

    def test_profile_context(self) -> None:
        """Проверка правильности контекста для profile"""
        first_object = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': TestViewsPosts.user.username},
            )
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(first_object)
        self.assertEqual(
            self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': TestViewsPosts.user.username},
                )
            ).context['author'],
            TestViewsPosts.user,
        )

    def test_post_detail(self) -> None:
        """Проверка правильности контекста для post_detail"""
        context = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'pk': TestViewsPosts.post.pk},
            )
        ).context['post']
        self.correct_page_obj_first_obj(context)

    def test_follow_index(self) -> None:
        """Проверка правильности контекста для follow_index"""
        Follow.objects.create(
            user=TestViewsPosts.follower_user, author=TestViewsPosts.user
        )
        context = self.follower_user_client.get(
            reverse('posts:follow_index')
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(context)

    def correct_fields_post_form(self, form) -> None:
        """Проверка соответствия полей для формы"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post(self) -> None:
        """Проверка правильности контекста для create_post"""
        form = self.authorized_client.get(
            reverse('posts:post_create')
        ).context['form']
        self.correct_fields_post_form(form)

    def test_post_edit(self) -> None:
        """Проверка правильности контекста для post_edit"""
        form = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'pk': TestViewsPosts.post.pk})
        ).context['form']
        self.correct_fields_post_form(form)
        self.assertEqual(
            self.authorized_client.get(
                reverse(
                    'posts:post_edit', kwargs={'pk': TestViewsPosts.post.pk}
                )
            ).context['is_edit'],
            True,
        )

    def test_extra_check(self) -> None:
        """Проверка, что уникальный пост попадает на нужные страницы"""
        self.assertEqual(
            Post.objects.filter(pk=TestViewsPosts.post.pk).exists(), True
        )
        response = {
            'index': reverse('posts:index'),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': TestViewsPosts.user.username},
            ),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': TestViewsPosts.group.slug}
            ),
        }
        for value in response.values():
            with self.subTest(value=value):
                self.assertEqual(
                    self.authorized_client.get(value).context['page_obj'][0],
                    TestViewsPosts.post,
                    msg=f'{value}',
                )

        self.assertEqual(
            len(
                (
                    self.authorized_client.get(
                        reverse(
                            'posts:group_list',
                            kwargs={'slug': TestViewsPosts.extra_group.slug},
                        ),
                    )
                ).context['page_obj']
            ),
            0,
        )

    def test_create_comment_authorized(self) -> None:
        """Проверка создания и отображения коммента на странице"""
        form_data = {'text': 'Комментарий'}
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': TestViewsPosts.post.pk}
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'pk': TestViewsPosts.post.pk}
            ),
        )
        self.assertEqual(
            self.authorized_client.get(
                reverse(
                    'posts:post_detail', kwargs={'pk': TestViewsPosts.post.pk}
                )
            ).context['comments'][0],
            Comment.objects.get(
                author=TestViewsPosts.user,
                text=form_data['text'],
                post=TestViewsPosts.post.pk,
            ),
        )

    def test_follow(self) -> None:
        """Проверка возможности подписки и отписки"""
        self.assertEqual(
            Follow.objects.filter(
                author=TestViewsPosts.user, user=TestViewsPosts.follower_user
            ).exists(),
            False,
        )
        self.follower_user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TestViewsPosts.user.username},
            )
        )
        self.assertEqual(
            Follow.objects.filter(
                author=TestViewsPosts.user, user=TestViewsPosts.follower_user
            ).exists(),
            True,
        )

        self.follower_user_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': TestViewsPosts.user.username},
            )
        )
        self.assertEqual(
            Follow.objects.filter(
                user=TestViewsPosts.follower_user,
                author=TestViewsPosts.user,
            ).exists(),
            False,
        )
