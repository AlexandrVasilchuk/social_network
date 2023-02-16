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
            author=PostURLTest.user_author,
            group=PostURLTest.group,
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(PostURLTest.user_author)
        cls.authorized_client_follower = Client()
        cls.authorized_client_follower.force_login(PostURLTest.user)
        cls.urls = {
            'add_comment': reverse(
                'posts:add_comment',
                kwargs={'pk': PostURLTest.post.pk},
            ),
            'follow_index': reverse('posts:follow_index'),
            'group_list': reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTest.group.slug},
            ),
            'post_create': reverse('posts:post_create'),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'pk': PostURLTest.post.pk},
            ),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'pk': PostURLTest.post.pk},
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostURLTest.user.username},
            ),
            'profile_follow': reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTest.user.username},
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTest.user.username},
            ),
            'index': reverse('posts:index'),
            'missing': '/non-exists/',
        }

    def setUp(self) -> None:
        cache.clear()

    def test_http_statuses(self) -> None:
        """Соответствие статуса страниц по указанным адресам для всех."""
        httpstatuses = (
            (self.urls.get('add_comment'), HTTPStatus.FOUND, self.client),
            (self.urls.get('follow_index'), HTTPStatus.FOUND, self.client),
            (self.urls.get('group_list'), HTTPStatus.OK, self.client),
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.client),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.client),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.client),
            (self.urls.get('profile'), HTTPStatus.OK, self.client),
            (self.urls.get('profile_follow'), HTTPStatus.FOUND, self.client),
            (self.urls.get('profile_unfollow'), HTTPStatus.FOUND, self.client),
            (self.urls.get('index'), HTTPStatus.OK, self.client),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.client),
            (
                self.urls.get('follow_index'),
                HTTPStatus.OK,
                self.authorized_client_author,
            ),
            (
                self.urls.get('post_create'),
                HTTPStatus.OK,
                self.authorized_client_author,
            ),
            (
                self.urls.get('post_edit'),
                HTTPStatus.OK,
                self.authorized_client_author,
            ),
            (
                self.urls.get('missing'),
                HTTPStatus.NOT_FOUND,
                self.authorized_client_author,
            ),
            (
                self.urls.get('follow_index'),
                HTTPStatus.OK,
                self.authorized_client_follower,
            ),
            (
                self.urls.get('post_create'),
                HTTPStatus.OK,
                self.authorized_client_follower,
            ),
            (
                self.urls.get('post_edit'),
                HTTPStatus.FOUND,
                self.authorized_client_follower,
            ),
        )

        for response, expected_status, client in httpstatuses:
            with self.subTest(value=expected_status):
                self.assertEqual(
                    client.get(response).status_code,
                    expected_status,
                    f'Страница {response} не доступна по нужному адресу!',
                )

    def test_templates(self) -> None:
        """Соответствие вызываемого шаблона."""
        templates = (
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                self.client,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.client,
            ),
            (self.urls.get('profile'), 'posts/profile.html', self.client),
            (self.urls.get('index'), 'posts/index.html', self.client),
            (
                self.urls.get('follow_index'),
                'posts/follow.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('index'),
                'posts/index.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('missing'),
                'core/404.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('follow_index'),
                'posts/follow.html',
                self.authorized_client_follower,
            ),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.authorized_client_follower,
            ),
        )

        for response, expected_template, client in templates:
            with self.subTest(value=expected_template):
                self.assertTemplateUsed(
                    client.get(response),
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
                self.authorized_client_follower,
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post_detail'),
                self.authorized_client_follower,
            ),
            (
                self.urls.get('profile_follow'),
                self.urls.get('follow_index'),
                self.authorized_client_follower,
            ),
            (
                self.urls.get('add_comment'),
                self.urls.get('post_detail'),
                self.authorized_client_author,
            ),
            (
                self.urls.get('profile_follow'),
                self.urls.get('follow_index'),
                self.authorized_client_author,
            ),
        )

        for response, expected_redirect, client in redirects:
            with self.subTest(value=expected_redirect):
                self.assertRedirects(
                    client.get(response, follow=True),
                    expected_redirect,
                    msg_prefix=f'Редирект для {response} не работает!',
                )
