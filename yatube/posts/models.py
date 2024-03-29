from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='заголовок',
    )
    slug = models.SlugField(unique=True, verbose_name='ссылка')
    description = models.TextField(verbose_name='описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='текст',
        help_text='Укажите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='название группы',
        related_name='posts',
        help_text='Укажите группу',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]
