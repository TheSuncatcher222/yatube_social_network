from django.contrib.auth.models import User
from django.core.cache import cache
from django.forms import models
from django.forms import fields
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from unittest import skip
from ..models import Group
from ..models import Post


class PostsViewsTests(TestCase):
    """Тестирование views приложения 'posts'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER = User.objects.create(username='Author')
        cls.group = Group.objects.create(
            description='Тестовое описание группы',
            slug='test_slug',
            title='Тестовое наименование группы',
        )
        cls.PAGE_POST_COUNT: int = 10
        cls.ONE_MORE_PAGE_POST_COUNT: int = 1
        cls.DIFFERENT_GROUPS_COUNT: int = 2
        cls.end_rage: int = (
            cls.PAGE_POST_COUNT
            + cls.ONE_MORE_PAGE_POST_COUNT
            * cls.DIFFERENT_GROUPS_COUNT)
        cls.post = Post.objects.bulk_create([Post(
            author=cls.USER,
            text=f'Тестовый пост без группы №{i}',)
            # Начинаем с 1, чтобы не был создан пост с номером 0
            for i in range(1, cls.end_rage)
        ])
        cls.post += Post.objects.bulk_create([Post(
            author=cls.USER,
            text=f'Тестовый пост с группой №{i}',
            group=cls.group)
            for i in range(1, cls.end_rage)
        ])
        cls.AUTHORIZED_CLIENT = Client()
        cls.AUTHORIZED_CLIENT.force_login(cls.USER)
        cls.SLUG = cls.group.slug
        cls.ID = Post.objects.latest('id').id

    def setUp(self):
        cache.clear()

    def test_url_use_templates(self) -> None:
        """Тест шаблонов для view функций"""
        test_dict: dict[str: str] = {
            reverse('posts:index'): 'includes/posts/index.html',
            reverse('posts:post_create'): 'includes/posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'group': PostsViewsTests.SLUG}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.ID}
            ): 'includes/posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.ID}
            ): 'includes/posts/create_post.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.USER}
            ): 'includes/posts/profile.html',
        }
        for value, expected in test_dict.items():
            response = PostsViewsTests.AUTHORIZED_CLIENT.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)
        test_dict[reverse('posts:post_create')] = (
            'includes/users/login.html'
        )
        test_dict[reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsViewsTests.ID}
        )] = 'includes/users/login.html'
        cache.clear()
        GUEST_CLIENT = Client()
        for value, expected in test_dict.items():
            response = GUEST_CLIENT.get(value, follow=True)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    @skip('Проверка постов производится в тесте paginator_for_index')
    def test_page_posts_index(self) -> None:
        """Тест URL 'posts:index'"""
        pass

    def test_page_posts_create_post(self) -> None:
        """Тест URL 'posts:create_post'"""
        response = self.AUTHORIZED_CLIENT.get(reverse('posts:post_create'))
        test_dict = {
            'group': models.ModelChoiceField,
            'text': fields.CharField,
        }
        for value, expected in test_dict.items():
            response_value = response.context['form'].fields[value]
            with self.subTest(value=value):
                self.assertIsInstance(response_value, expected)

    @skip('Проверка постов производится в тесте paginator_for_group_list')
    def test_page_posts_group_list(self) -> None:
        """Тест URL 'posts:group_list'"""
        pass

    def test_page_post_post_detail(self) -> None:
        """Тест URL 'post:post_detail'"""
        response = self.AUTHORIZED_CLIENT.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.ID}
            )
        )
        count = Post.objects.filter(author=PostsViewsTests.USER).count()
        text = Post.objects.get(id=PostsViewsTests.ID).text
        test_dict = {
            count: response.context['posts_count'],
            text: response.context['post'].text,
        }
        for value, expected in test_dict.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
        self.assertIsInstance(
            response.context['comments_form'].fields['text'],
            fields.CharField)

    def test_page_post_post_edit(self) -> None:
        """Тест URL 'post:post_edit'"""
        response = self.AUTHORIZED_CLIENT.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.ID}
            )
        )
        test_form_dict = {
            'group': models.ModelChoiceField,
            'text': fields.CharField,
        }
        for value, expected in test_form_dict.items():
            response_value = response.context['form'].fields[value]
            with self.subTest(value=value):
                self.assertIsInstance(response_value, expected)
        test_dict = {
            'is_edit': True,
            'post_id': PostsViewsTests.ID,
        }
        for value, expected in test_dict.items():
            response_value = response.context[value]
            with self.subTest(value=value):
                self.assertEqual(response_value, expected)

    def test_page_post_profile(self) -> None:
        """Тест URL 'post:profile'"""
        response = self.AUTHORIZED_CLIENT.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.USER}
            )
        )
        test_dict = {
            'author': str(PostsViewsTests.USER),
            # 'page_obj': Проверка производится в тесте paginator_for_profile
        }
        for field, expected in test_dict.items():
            with self.subTest(field=field):
                response_value = str(response.context[field])
                self.assertEqual(response_value, expected)

    def test_paginator_for_index(self) -> None:
        """Тест paginator для 'posts:index'"""
        # Постов всего 22, по 10 штук на страницу
        test_dict = {
            1: 10,
            2: 10,
            3: 2,
        }
        for field, expected in test_dict.items():
            with self.subTest(field=field):
                start_index: int = 0
                end_index: int = 0
                if field == 1:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse('posts:index')
                    )
                    end_index = 10
                if field == 2:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse('posts:index') + f'?page={field}'
                    )
                    start_index = 10
                    end_index = 20
                if field == 3:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse('posts:index') + f'?page={field}'
                    )
                    start_index = 20
                    end_index = 22
                response_value = len(response.context['page_obj'])
                self.assertEqual(response_value, expected)
                response_value = list(response.context['page_obj'])
                expected = list(Post.objects.all()[start_index:end_index])
                self.assertEqual(response_value, expected)

    def test_paginator_for_group_list(self) -> None:
        """Тест paginator для 'posts:group_list'"""
        # Постов с 'test_slug' всего 11, по 10 штук на страницу
        test_dict = {
            1: 10,
            2: 1,
        }
        for field, expected in test_dict.items():
            with self.subTest(field=field):
                start_index: int = 0
                end_index: int = 0
                if field == 1:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse(
                            'posts:group_list',
                            kwargs={'group': PostsViewsTests.SLUG}
                        )
                    )
                    end_index = 10
                if field == 2:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse(
                            'posts:group_list',
                            kwargs={'group': PostsViewsTests.SLUG}
                        ) + f'?page={field}'
                    )
                    start_index = 10
                    end_index = 20
                response_value = len(response.context['page_obj'])
                self.assertEqual(response_value, expected)
                response_value = list(response.context['page_obj'])
                expected = list(Post.objects.filter(
                    group=PostsViewsTests.group
                )[start_index:end_index]
                )
                self.assertEqual(response_value, expected)

    def test_paginator_for_profile(self) -> None:
        """Тест paginator для 'posts:profile'"""
        # Постов автора всего 22, по 10 штук на страницу
        test_dict = {
            1: 10,
            2: 10,
            3: 2,
        }
        for field, expected in test_dict.items():
            with self.subTest(field=field):
                start_index: int = 0
                end_index: int = 0
                if field == 1:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse(
                            'posts:profile',
                            kwargs={'username': str(PostsViewsTests.USER)}
                        )
                    )
                    end_index = 10
                if field == 2:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse(
                            'posts:profile',
                            kwargs={'username': str(PostsViewsTests.USER)}
                        ) + f'?page={field}'
                    )
                    start_index = 10
                    end_index = 20
                if field == 3:
                    response = PostsViewsTests.AUTHORIZED_CLIENT.get(
                        reverse(
                            'posts:profile',
                            kwargs={'username': str(PostsViewsTests.USER)}
                        ) + f'?page={field}'
                    )
                    start_index = 20
                    end_index = 22
                response_value = len(response.context['page_obj'])
                self.assertEqual(response_value, expected)
                response_value = list(response.context['page_obj'])
                expected = list(Post.objects.all()[start_index:end_index])
                self.assertEqual(response_value, expected)

    def test_cache_for_index(self) -> None:
        """Тест cache для страницы 'posts:index'"""
        response = PostsViewsTests.AUTHORIZED_CLIENT.get(
            reverse('posts:index')
        )
        old_content = response.content
        new_post_data = {'text': 'Пост для тестирования cache'}
        PostsViewsTests.AUTHORIZED_CLIENT.post(
            reverse('posts:post_create'),
            data=new_post_data,
        )
        new_post_id = Post.objects.latest('id').id
        self.assertEqual(new_post_id, PostsViewsTests.ID + 1)
        response = PostsViewsTests.AUTHORIZED_CLIENT.get(
            reverse('posts:index')
        )
        cached_content = response.content
        Post.objects.filter(id=new_post_id).delete()
        response = PostsViewsTests.AUTHORIZED_CLIENT.get(
            reverse('posts:index')
        )
        new_content = response.content
        self.assertEqual(new_content, cached_content)
        cache.clear()
        response = PostsViewsTests.AUTHORIZED_CLIENT.get(
            reverse('posts:index')
        )
        uncached_content = response.content
        self.assertEqual(uncached_content, old_content)
