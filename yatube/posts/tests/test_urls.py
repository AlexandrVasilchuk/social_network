from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_author = mixer.blend(User)

        cls.group = mixer.blend('posts.Group')
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.user_author,
            group=cls.group,
        )

        cls.author, cls.follower = Client(), Client()
        cls.author.force_login(cls.user_author)
        cls.follower.force_login(cls.user)

        cls.urls = {
            'add_comment': reverse(
                'posts:add_comment',
                args=(cls.post.pk,),
            ),
            'follow_index': reverse('posts:follow_index'),
            'group_list': reverse(
                'posts:group_list',
                args=(cls.group.slug,),
            ),
            'post_create': reverse('posts:post_create'),
            'post_detail': reverse(
                'posts:post_detail',
                args=(cls.post.pk,),
            ),
            'post_edit': reverse(
                'posts:post_edit',
                args=(cls.post.pk,),
            ),
            'profile': reverse(
                'posts:profile',
                args=(cls.user.username,),
            ),
            'profile_follow': reverse(
                'posts:profile_follow',
                args=(cls.user.username,),
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                args=(cls.user.username,),
            ),
            'index': reverse('posts:index'),
            'missing': '/non-exists/',
        }

    def test_http_statuses(self) -> None:
        """Соответствие статуса страниц по указанным адресам для всех."""
        httpstatuses = (
            ('add_comment', HTTPStatus.FOUND, self.client),
            ('follow_index', HTTPStatus.FOUND, self.client),
            ('group_list', HTTPStatus.OK, self.client),
            ('post_create', HTTPStatus.FOUND, self.client),
            ('post_detail', HTTPStatus.OK, self.client),
            ('post_edit', HTTPStatus.FOUND, self.client),
            ('profile', HTTPStatus.OK, self.client),
            ('profile_follow', HTTPStatus.FOUND, self.client),
            ('profile_unfollow', HTTPStatus.FOUND, self.client),
            ('index', HTTPStatus.OK, self.client),
            ('missing', HTTPStatus.NOT_FOUND, self.client),
            (
                'follow_index',
                HTTPStatus.OK,
                self.author,
            ),
            (
                'post_create',
                HTTPStatus.OK,
                self.author,
            ),
            (
                'post_edit',
                HTTPStatus.OK,
                self.author,
            ),
            (
                'missing',
                HTTPStatus.NOT_FOUND,
                self.author,
            ),
            (
                'follow_index',
                HTTPStatus.OK,
                self.follower,
            ),
            (
                'post_create',
                HTTPStatus.OK,
                self.follower,
            ),
            (
                'post_edit',
                HTTPStatus.FOUND,
                self.follower,
            ),
        )

        for response, expected_status, client in httpstatuses:
            with self.subTest(value=expected_status):
                self.assertEqual(
                    client.get(self.urls.get(response)).status_code,
                    expected_status,
                    f'Страница {response} не доступна по нужному адресу!',
                )

    def test_templates(self) -> None:
        """Соответствие вызываемого шаблона."""
        templates = (
            (
                'group_list',
                'posts/group_list.html',
                self.client,
            ),
            (
                'post_detail',
                'posts/post_detail.html',
                self.client,
            ),
            ('profile', 'posts/profile.html', self.client),
            ('index', 'posts/index.html', self.client),
            (
                'follow_index',
                'posts/follow.html',
                self.author,
            ),
            (
                'group_list',
                'posts/group_list.html',
                self.author,
            ),
            (
                'post_create',
                'posts/create_post.html',
                self.author,
            ),
            (
                'post_detail',
                'posts/post_detail.html',
                self.author,
            ),
            (
                'post_edit',
                'posts/create_post.html',
                self.author,
            ),
            (
                'profile',
                'posts/profile.html',
                self.author,
            ),
            (
                'index',
                'posts/index.html',
                self.author,
            ),
            (
                'missing',
                'core/404.html',
                self.author,
            ),
            (
                'follow_index',
                'posts/follow.html',
                self.follower,
            ),
            (
                'post_create',
                'posts/create_post.html',
                self.follower,
            ),
        )

        for response, expected_template, client in templates:
            with self.subTest(value=expected_template):
                self.assertTemplateUsed(
                    client.get(self.urls.get(response)),
                    expected_template,
                    f'Страница {response} не вызывает нужный шаблон!',
                )
            cache.clear()

    def test_redirects(self) -> None:
        """Проверка редиректа для пользователей."""
        redirects = (
            (
                self.urls.get('add_comment'),
                redirect_to_login(next=self.urls.get('add_comment')).url,
                self.client,
            ),
            (
                self.urls.get('follow_index'),
                redirect_to_login(next=self.urls.get('follow_index')).url,
                self.client,
            ),
            (
                self.urls.get('post_create'),
                redirect_to_login(next=self.urls.get('post_create')).url,
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                redirect_to_login(next=self.urls.get('post_edit')).url,
                self.client,
            ),
            (
                self.urls.get('profile_follow'),
                redirect_to_login(next=self.urls.get('profile_follow')).url,
                self.client,
            ),
            (
                self.urls.get('profile_unfollow'),
                redirect_to_login(next=self.urls.get('profile_unfollow')).url,
                self.client,
            ),
            (
                self.urls.get('add_comment'),
                self.urls.get('post_detail'),
                self.follower,
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post_detail'),
                self.follower,
            ),
            (
                self.urls.get('profile_follow'),
                self.urls.get('follow_index'),
                self.follower,
            ),
            (
                self.urls.get('add_comment'),
                self.urls.get('post_detail'),
                self.author,
            ),
            (
                self.urls.get('profile_follow'),
                self.urls.get('follow_index'),
                self.author,
            ),
        )

        for response, expected_redirect, client in redirects:
            with self.subTest(value=expected_redirect):
                self.assertRedirects(
                    client.get(response, follow=True),
                    expected_redirect,
                    msg_prefix=f'Редирект для {response} не работает!',
                )
