from django.contrib.auth.models import User
from django.test import TestCase
from unittest import skip
from posts.models import Follow
from posts.models import Comment
from posts.models import Group
from posts.models import Post

POST_TEXT = ('Тестовый текст тестового поста, в котором более 30 (33) '
              + 'допустимых слов, и при этом абсолютно не несет в себе '
              + 'никакого смысла, кроме того, чтобы проверить, работает ли '
              + 'функция для обрезки текста в __str__'
              )
POST_STR = ('Тестовый текст тестового поста, в котором более 30 (33) '
                  + 'допустимых слов, и при этом абсолютно не несет в себе '
                  + 'никакого смысла, кроме того, чтобы проверить, работает ли '
                  + 'функция для обрезки ...')


class PostModelTest(TestCase):
    """Тест моделей Group и Post приложения 'posts'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER = User.objects.create(username='Тестовый автор')
        cls.FOLLOWER = User.objects.create(
            username='Подписчик'
        )
        cls.group = Group.objects.create(
            description='Тестовое описание группы',
            slug='test_slug',
            title='Тестовое наименование группы',
        )
        cls.post = Post.objects.create(
            author=cls.USER,
            group=cls.group,
            text=POST_TEXT,
        )
        cls.comment = Comment.objects.create(
            author=cls.USER,
            post=cls.post,
            text='Классный тестовый текст! И комментарий!!',
        )
        cls.follow = Follow.objects.create(
            author=cls.USER,
            user=cls.FOLLOWER,
        )

    def test_models_have_correct_object_names(self) -> None:
        """Проверка, что у моделей корректно работает __str__"""
        test_dict = {
            str(PostModelTest.comment): 'Классный тестовый текст! И комментарий!!',
            str(PostModelTest.follow): 'Тестовый автор',
            str(PostModelTest.group): 'Тестовое наименование группы',
            str(PostModelTest.post): POST_STR,
        }
        for task, expected_value in test_dict.items():
            with self.subTest(field=task):
                self.assertEqual(task, expected_value)

    @skip('Already tested in test_models_have_correct_object_names for Post ')
    def test_str_output_cut(self) -> None:
        """Проверка усечения выходного текста моделей"""
        pass

    def test_models_fields(self) -> None:
        """Проверка полей моделей"""
        test_dict = {
            str(PostModelTest.comment.author): 'Тестовый автор',
            str(PostModelTest.comment.post): POST_STR,
            PostModelTest.comment.text: (
                'Классный тестовый текст! И комментарий!!'
            ),
            PostModelTest.comment._meta.get_field('author').verbose_name: (
                'Автор комментария'
            ),
            PostModelTest.comment._meta.get_field('pub_date').verbose_name: (
                'Дата публикации'
            ),
            PostModelTest.comment._meta.get_field('post').verbose_name: (
                'Комментируемый пост'
            ),
            PostModelTest.comment._meta.get_field('text').verbose_name: (
                'Комментарий'
            ),
            PostModelTest.comment._meta.default_related_name: 'comments',
            PostModelTest.comment._meta.verbose_name: 'комментарий',
            PostModelTest.comment._meta.verbose_name_plural: 'Комментарии',
            str(PostModelTest.follow.author): 'Тестовый автор',
            str(PostModelTest.follow.user): 'Подписчик',
            PostModelTest.follow._meta.get_field('author').verbose_name: (
                'автор'
            ),
            PostModelTest.follow._meta.get_field('user').verbose_name: (
                'подписчик'
            ),
            PostModelTest.follow._meta.verbose_name: 'подписку',
            PostModelTest.follow._meta.verbose_name_plural: 'Подписки',
            PostModelTest.group.description: 'Тестовое описание группы',
            PostModelTest.group.slug: 'test_slug',
            PostModelTest.group.title: 'Тестовое наименование группы',
            PostModelTest.group._meta.get_field('description').verbose_name: (
                'Описание группы'
            ),
            PostModelTest.group._meta.get_field('slug').verbose_name: (
                'Уникальный URL группы'
            ),
            PostModelTest.group._meta.get_field('title').verbose_name: (
                'Названия группы'
            ),
            PostModelTest.group._meta.verbose_name: 'группу',
            PostModelTest.group._meta.verbose_name_plural: 'группы',
            str(PostModelTest.post.author): 'Тестовый автор',
            str(PostModelTest.post.group): 'Тестовое наименование группы',
            PostModelTest.post.text: POST_TEXT,
            PostModelTest.post._meta.get_field('author').verbose_name: (
                'Автор поста'
            ),
            PostModelTest.post._meta.get_field('group').help_text: (
                'Укажите группу, к которой будет относится пост'
            ),
            PostModelTest.post._meta.get_field('group').verbose_name: (
                'Группа (не обязательно)'
            ),
            PostModelTest.post._meta.get_field('image').help_text: (
                'Прикрепите картинку (не обязательно)'
            ),
            PostModelTest.post._meta.get_field('pub_date').verbose_name: (
                'Дата публикации'
            ),
            PostModelTest.post._meta.get_field('text').help_text: (
                'Введите текст вашего поста'
            ),
            PostModelTest.post._meta.get_field('text').verbose_name: (
                'Текст поста'
            ),
            PostModelTest.post._meta.verbose_name: 'пост',
            PostModelTest.post._meta.verbose_name_plural: 'Посты',
        }
        for field, expected_value in test_dict.items():
            with self.subTest(field=expected_value):
                self.assertEqual(field, expected_value)
