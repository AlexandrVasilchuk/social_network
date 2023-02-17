from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()

AMMOUNT_OBJECTS = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.group = mixer.blend('posts.Group')
        mixer.cycle(AMMOUNT_OBJECTS).blend(
            'posts.Post',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_paginator_separator(self) -> None:
        """Проверка корректного разделения постов паджинатором."""
        response_values = {
            reverse('posts:index'): settings.PAGE_SIZE,
            reverse('posts:index')
            + '?page=2': AMMOUNT_OBJECTS
            - settings.PAGE_SIZE,
            reverse(
                'posts:group_list',
                args=(self.group.slug,),
            ): settings.PAGE_SIZE,
            reverse(
                'posts:group_list',
                args=(self.group.slug,),
            )
            + '?page=2': AMMOUNT_OBJECTS
            - settings.PAGE_SIZE,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            ): settings.PAGE_SIZE,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            )
            + '?page=2': AMMOUNT_OBJECTS
            - settings.PAGE_SIZE,
        }

        for response, value in response_values.items():
            with self.subTest(value=value):
                self.assertEqual(
                    len(
                        (self.authorized_client.get(response)).context[
                            'page_obj'
                        ],
                    ),
                    value,
                )
