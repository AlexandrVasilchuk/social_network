from django.contrib.auth import get_user_model
from django.db import models

from yatube.models import AbstractedModel

User = get_user_model()

POST_SYMBOLS_LIMITATION = 15


class Group(models.Model):
    titlemaxlenght = 200

    title = models.CharField('заголовок', max_length=titlemaxlenght)
    slug = models.SlugField('имя группы', unique=True)
    description = models.TextField('описание')

    def __str__(self) -> str:
        return self.title


class Post(AbstractedModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
    )
    image = models.ImageField(
        'картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta(AbstractedModel.Meta):
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[:POST_SYMBOLS_LIMITATION]


class Comment(AbstractedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta(AbstractedModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        default_related_name = 'comments'

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_author',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'Пользователь {self.user.username} '
            f'подписан на автора {self.author.username}'
        )
