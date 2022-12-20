from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel


def str_output_cut(text, author):
    """Сокращает выводимый текст в __str__ до N слов"""
    slit_text: list = text.split(' ')
    words_to_preview: int = 5
    if len(slit_text) > words_to_preview:
        slit_text = slit_text[:words_to_preview]
        text = ' '.join(slit_text) + ' ...'
    new_line: str = '\n'
    return_string: str = (
        f'Автор: {author}{new_line}'
        + f'Текст: {text}'
    )
    return return_string


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        """Отображает информацию об объекте (классе)"""
        return str(self.author)


class Group(models.Model):
    description = models.TextField(verbose_name='Описание группы')
    slug = models.SlugField(unique=True,
                            verbose_name='Уникальный URL группы'
                            )
    title = models.CharField(unique=True,
                             max_length=200,
                             verbose_name='Названия группы',
                             )

    class Meta:
        verbose_name = 'группу'
        verbose_name_plural = 'группы'

    def __str__(self):
        """Отображает информацию об объекте (классе)"""
        return self.title


class Post(BaseModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        help_text='Укажите группу, к которой будет относится пост',
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа (не обязательно)',
    )
    image = models.ImageField(
        'Картинка',
        blank=True,
        help_text='Прикрепите картинку (не обязательно)',
        upload_to='posts/',
    )
    text = models.TextField(
        help_text='Введите текст вашего поста',
        verbose_name='Текст поста',
    )

    class Meta:
        default_related_name = 'posts'
        ordering = ['-pub_date']
        verbose_name = 'пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Отображает информацию об объекте (классе)"""
        return str_output_cut(self.text, self.author)


class Comment(BaseModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост',
    )
    text = models.TextField(
        help_text='Введите текст вашего комментария',
        verbose_name='Комментарий',
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ['-pub_date']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Отображает информацию об объекте (классе)"""
        return str_output_cut(self.text, self.author)
