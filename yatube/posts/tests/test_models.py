from django.contrib.auth.models import User
from django.test import TestCase
from unittest import skip
from posts.models import Follow
from posts.models import Comment
from posts.models import Group
from posts.models import Post

text_dict: dict[str, str] = {
    'user_username': 'Тестовый автор',
    'follower_username': 'Подписчик',
    'group_description': 'Тестовое описание группы',
    'group_slug': 'test_slug',
    'group_title': 'Тестовое наименование группы',
    'post_text': 'Тестовый текст тестового поста, который более 5 слов',
    'comment_text': 'Классный тестовый текст! И комментарий!!',
}


class PostModelTest(TestCase):
    """Тест моделей Group и Post приложения 'posts'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER = User.objects.create(username=text_dict['user_username'])
        cls.FOLLOWER = User.objects.create(
            username=text_dict['follower_username']
        )
        cls.group = Group.objects.create(
            description=text_dict['group_description'],
            slug=text_dict['group_slug'],
            title=text_dict['group_title'],
        )
        cls.post = Post.objects.create(
            author=cls.USER,
            group=cls.group,
            text=text_dict['post_text'],
        )
        cls.comment = Comment.objects.create(
            author=cls.USER,
            post=cls.post,
            text=text_dict['comment_text'],
        )
        cls.follow = Follow.objects.create(
            author=cls.USER,
            user=cls.FOLLOWER,
        )
        cls.NEW_LINE: str = '\n'
        cls.STR_POST = (
            f'Автор: Тестовый автор{cls.NEW_LINE}'
            + 'Текст: Тестовый текст тестового поста, который ...'
        )

    def test_models_have_correct_object_names(self) -> None:
        """Проверка, что у моделей корректно работает __str__"""
        STR_COMMENT = (
            f'Автор: Тестовый автор{PostModelTest.NEW_LINE}'
            + 'Текст: Классный тестовый текст! И комментарий!!'
        )
        test_dict = {
            str(PostModelTest.comment): STR_COMMENT,
            str(PostModelTest.follow): text_dict['user_username'],
            str(PostModelTest.group): text_dict['group_title'],
            str(PostModelTest.post): PostModelTest.STR_POST,
        }
        for task, expected_value in test_dict.items():
            with self.subTest(field=task):
                self.assertEqual(task, expected_value)

    @skip('Already tested in test_models_have_correct_object_names for Post ')
    def test_str_output_cut(self) -> None:
        """Проверка усечения выходного текста у моделей"""
        pass

    def test_models_fields(self) -> None:
        """Проверка полей у моделей"""
        test_dict = {
            str(PostModelTest.comment.author): text_dict['user_username'],
            str(PostModelTest.comment.post): PostModelTest.STR_POST,
            PostModelTest.comment.text: text_dict['comment_text'],
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
            str(PostModelTest.follow.author): text_dict['user_username'],
            str(PostModelTest.follow.user): text_dict['follower_username'],
            PostModelTest.follow._meta.get_field('author').verbose_name: (
                'автор'
            ),
            PostModelTest.follow._meta.get_field('user').verbose_name: (
                'подписчик'
            ),
            PostModelTest.follow._meta.verbose_name: 'подписку',
            PostModelTest.follow._meta.verbose_name_plural: 'Подписки',
            PostModelTest.group.description: text_dict['group_description'],
            PostModelTest.group.slug: text_dict['group_slug'],
            PostModelTest.group.title: text_dict['group_title'],
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
            str(PostModelTest.post.author): text_dict['user_username'],
            str(PostModelTest.post.group): text_dict['group_title'],
            PostModelTest.post.text: text_dict['post_text'],
            PostModelTest.post._meta.get_field('author').verbose_name: (
                'Автор поста'
            ),
            PostModelTest.post._meta.get_field('group').help_text: (
                'Укажите группу, к которой будет относится пост'
            ),
            PostModelTest.post._meta.get_field('group').verbose_name: (
                'Группа (не обязательно)'
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
