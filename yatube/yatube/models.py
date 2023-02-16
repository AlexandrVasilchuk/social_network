from django.db import models


class AbstractedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания и текст."""

    pub_date = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True,
    )
    text = models.TextField(
        verbose_name='текст',
        max_length=200,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
