import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestViewsPosts(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(
            Post,
            author=cls.user_author,
            group=cls.group,
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user_author)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        cache.clear()

    def correct_page_obj_first_obj(self, first_object: Post) -> None:
        """Проверка соответствия поста на странице.

        Args:
            first_object: Первый на странице объект модели Post.
        """
        fields_to_check = {
            first_object.pk: self.post.pk,
            first_object.author.username: self.user_author.username,
            first_object.group.title: self.group.title,
            first_object.text: self.post.text,
            first_object.image: self.post.image,
        }
        for field, expected in fields_to_check.items():
            with self.subTest(expected=expected):
                self.assertEqual(field, expected)

    def test_index_context(self) -> None:
        """Шаблон index сформирован с правильным контекстом."""
        first_object = self.authorized_client_author.get(
            reverse('posts:index'),
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(first_object)

    def test_group_list_context(self) -> None:
        """Проверка правильности контекста для group_list."""
        first_object = self.authorized_client_author.get(
            reverse('posts:group_list', args=(self.group.slug,)),
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(first_object)

        self.assertEqual(
            self.authorized_client_author.get(
                reverse(
                    'posts:group_list',
                    args=(self.group.slug,),
                ),
            ).context['group'],
            self.group,
        )

    def test_profile_context(self) -> None:
        """Проверка правильности контекста для profile."""
        follower_authorized_client = Client()
        follower_authorized_client.force_login(user=mixer.blend(User))
        first_object = self.authorized_client_author.get(
            reverse(
                'posts:profile',
                args=(self.user_author.username,),
            ),
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(first_object)
        self.assertEqual(
            self.authorized_client_author.get(
                reverse(
                    'posts:profile',
                    args=(self.user_author.username,),
                ),
            ).context['author'],
            self.user_author,
        )

        self.assertEqual(
            self.authorized_client_author.get(
                reverse(
                    'posts:profile',
                    args=(self.user_author.username,),
                ),
            ).context['following'],
            False,
        )

        self.assertEqual(
            follower_authorized_client.get(
                reverse(
                    'posts:profile',
                    args=(self.user_author.username,),
                ),
            ).context['following'],
            False,
        )

    def test_follow_usage(self) -> None:
        """Проверка возможности подписки/отписки для разных клиентов."""
        user, user_client = mixer.blend(User), Client()
        user_client.force_login(user=user)

        user_client.get(
            reverse('posts:profile_follow', args=(self.user_author.username,)),
        )
        self.assertTrue(
            Follow.objects.filter(
                author__following__user=user,
                author=self.user_author,
            ).exists(),
        )
        user_client.get(
            reverse('posts:profile_follow', args=(self.user_author.username,)),
        )
        self.assertEqual(
            Follow.objects.filter(
                author__following__user=user,
                author=self.user_author,
            ).count(),
            1,
        )
        user_client.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.user_author.username,),
            ),
        )
        self.assertEqual(
            Follow.objects.filter(
                author__following__user=user,
                author=self.user_author,
            ).exists(),
            False,
        )

        self.authorized_client_author.get(
            reverse('posts:profile_follow', args=(self.user_author.username,)),
        )
        self.assertEqual(
            Follow.objects.filter(
                author__following__user=user,
                author=self.user_author,
            ).exists(),
            False,
        )

        self.assertRedirects(
            self.client.get(
                reverse(
                    'posts:profile_follow',
                    args=(self.user_author.username,),
                ),
            ),
            redirect_to_login(
                next=reverse(
                    'posts:profile_follow',
                    args=(self.user_author.username,),
                ),
            ).url,
        )

    def test_post_detail(self) -> None:
        """Проверка правильности контекста для post_detail."""
        context = self.authorized_client_author.get(
            reverse(
                'posts:post_detail',
                args=(self.post.pk,),
            ),
        ).context['post']
        self.correct_page_obj_first_obj(context)

    def test_follow_index(self) -> None:
        """Проверка правильности контекста для follow_index."""
        follower_user = mixer.blend(User)
        follower_user_client = Client()
        follower_user_client.force_login(user=follower_user)
        Follow.objects.create(user=follower_user, author=self.user_author)
        context = follower_user_client.get(
            reverse('posts:follow_index'),
        ).context['page_obj'][0]
        self.correct_page_obj_first_obj(context)

    def correct_fields_post_form(self, form: forms.Form) -> None:
        """Проверка соответствия полей для формы.

        Args:
            form: Поле формы переданной на вызванную страницу.
        """
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(form.fields[value], expected)

    def test_create_post(self) -> None:
        """Проверка правильности контекста для create_post."""
        form = self.authorized_client_author.get(
            reverse('posts:post_create'),
        ).context['form']
        self.correct_fields_post_form(form)

    def test_post_edit(self) -> None:
        """Проверка правильности контекста для post_edit."""
        form = self.authorized_client_author.get(
            reverse('posts:post_edit', args=(self.post.pk,)),
        ).context['form']
        self.correct_fields_post_form(form)
        self.assertTrue(
            self.authorized_client_author.get(
                reverse('posts:post_edit', args=(self.post.pk,)),
            ).context['is_edit'],
        )

    def test_extra_check(self) -> None:
        """Проверка, что уникальный пост попадает на нужные страницы."""
        extra_group = mixer.blend(Group)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
        response = {
            'index': reverse('posts:index'),
            'profile': reverse(
                'posts:profile',
                args=(self.user_author.username,),
            ),
            'group_list': reverse(
                'posts:group_list',
                args=(self.group.slug,),
            ),
        }
        for value in response.values():
            with self.subTest(value=value):
                self.assertEqual(
                    self.authorized_client_author.get(value).context[
                        'page_obj'
                    ][0],
                    self.post,
                    msg=f'{value}',
                )

        self.assertEqual(
            len(
                (
                    self.authorized_client_author.get(
                        reverse(
                            'posts:group_list',
                            args=(extra_group.slug,),
                        ),
                    )
                ).context['page_obj'],
            ),
            0,
        )

    def test_create_comment_authorized(self) -> None:
        """Проверка создания и отображения коммента на странице."""
        form_data = {
            'text': 'Комментарий',
        }
        response = self.authorized_client_author.post(
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
        self.assertEqual(
            self.authorized_client_author.get(
                reverse(
                    'posts:post_detail',
                    args=(self.post.pk,),
                ),
            ).context['comments'][0],
            Comment.objects.get(
                author=self.user_author,
                text=form_data['text'],
                post=self.post.pk,
            ),
        )
