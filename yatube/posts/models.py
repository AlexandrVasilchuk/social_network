from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

POST_SYMBOLS_LIMITATION = 15


class Group(models.Model):
    titlemaxlenght = 200

    title = models.CharField('заголовок', max_length=titlemaxlenght)
    slug = models.SlugField('имя группы', unique=True)
    description = models.TextField('описание')

    def __str__(self) -> models.CharField:
        return self.title


class Post(models.Model):
    text = models.TextField('текст поста', help_text='Текст нового поста')
    pub_date = models.DateTimeField('время публикации', auto_now_add=True)
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
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[:POST_SYMBOLS_LIMITATION]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        'комментарий',
        help_text='Оставьте свой комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField('время комментария', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_author'
            ),
        ]

    def __str__(self) -> str:
        return (
            f'Пользователь {self.user.username} '
            f'подписан на автора {self.author.username}'
        )
