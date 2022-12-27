from core.constants import PAGE_POST_COUNT
from django.contrib.auth.models import User
from django.core.cache import cache
from django.forms import models
from django.forms import fields
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from unittest import skip
from posts.models import Comment
from posts.models import Follow
from posts.models import Group
from posts.models import Post

ONE_MORE_PAGE_POST_COUNT: int = 1
DIFFERENT_GROUPS_COUNT: int = 2


class PostsViewsTests(TestCase):
    """Тестирование views приложения 'posts'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER_1 = User.objects.create(username='Author_1')
        cls.USER_2 = User.objects.create(username='Author_2')
        cls.GROUP = Group.objects.create(
            description='Тестовое описание группы',
            slug='test_slug',
            title='Тестовое наименование группы',
        )
        cls.end_rage_bulk_create = (
            PAGE_POST_COUNT
            + ONE_MORE_PAGE_POST_COUNT
            * DIFFERENT_GROUPS_COUNT
        )
        cls.post = Post.objects.bulk_create(
            Post(
                author=cls.USER_1,
                text=f'Тестовый пост без группы №{i}',
                group=cls.GROUP
            )
            for i in range(1, cls.end_rage_bulk_create)
        )
        cls.post += Post.objects.bulk_create(
            Post(
                author=cls.USER_1,
                text=f'Тестовый пост с группой №{i}',
            )
            for i in range(1, cls.end_rage_bulk_create)
        )
        cls.GUEST_CLIENT = Client()
        cls.AUTHORIZED_CLIENT_1 = Client()
        cls.AUTHORIZED_CLIENT_1.force_login(cls.USER_1)
        cls.AUTHORIZED_CLIENT_2 = Client()
        cls.AUTHORIZED_CLIENT_2.force_login(cls.USER_2)
        cls.SLUG = cls.GROUP.slug
        cls.POST_ID = Post.objects.latest('id').id
        cls.COMMENT = Comment.objects.create(
            author=cls.USER_1,
            post=Post.objects.get(id=cls.POST_ID),
            text='Классный тестовый текст! И комментарий!!',
        )
        cls.COMMENT_ID = Comment.objects.latest('id').id

    def setUp(self):
        cache.clear()

    def test_url_use_templates(self) -> None:
        """Тест шаблонов для view функций"""
        test_dict_authorized: dict[str: str] = {
            reverse('posts:index'): 'includes/posts/index.html',
            reverse('posts:post_create'): 'includes/posts/create_post.html',
            reverse('posts:follow_index'): 'includes/posts/follow.html',
            reverse(
                'posts:group_list',
                kwargs={'group': PostsViewsTests.SLUG}
            ): 'includes/posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.POST_ID}
            ): 'includes/posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.POST_ID}
            ): 'includes/posts/create_post.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.USER_1}
            ): 'includes/posts/profile.html',
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostsViewsTests.USER_2}
            ): 'includes/posts/profile.html',
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostsViewsTests.USER_2}
            ): 'includes/posts/profile.html',
        }
        test_dict_authorized_follow = {
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostsViewsTests.POST_ID}
            ): 'includes/posts/post_detail.html',
            reverse(
                'posts:delete_comment',
                kwargs={'comment_id': PostsViewsTests.COMMENT_ID}
            ): 'includes/posts/post_detail.html',
        }
        test_list_guest: list[reverse] = [
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostsViewsTests.POST_ID}
            ),
            reverse(
                'posts:delete_comment',
                kwargs={'comment_id': PostsViewsTests.COMMENT_ID}
            ),
            reverse('posts:follow_index'),
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.POST_ID}
            ),
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostsViewsTests.USER_2}
            ),
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostsViewsTests.USER_2}
            ),
        ]
        test_dict_guest = test_dict_authorized.copy()
        for path in test_list_guest:
            test_dict_guest[path] = ('includes/users/login.html')
        response_2 = PostsViewsTests.AUTHORIZED_CLIENT_2.get(
            reverse(
                'posts:delete_comment',
                kwargs={'comment_id': PostsViewsTests.COMMENT_ID}
            ),
            follow=True
        )
        self.assertTemplateUsed(response_2, 'includes/posts/post_detail.html')
        for value, expected in test_dict_authorized.items():
            response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(value)
            with self.subTest(value=f'AUTHORIZED_CLIENT: {value}'):
                self.assertTemplateUsed(response, expected)
        for value, expected in test_dict_authorized_follow.items():
            response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
                value,
                follow=True)
            with self.subTest(value=f'AUTHORIZED_CLIENT_follow: {value}'):
                self.assertTemplateUsed(response, expected)
        cache.clear()
        for value, expected in test_dict_guest.items():
            response = PostsViewsTests.GUEST_CLIENT.get(value, follow=True)
            with self.subTest(value=f'GUEST_CLIENT: {value}'):
                self.assertTemplateUsed(response, expected)

    @skip('Проверка постов производится в тесте paginator_for_index')
    def test_page_posts_index(self) -> None:
        """Тест URL 'posts:index'"""
        pass

    def test_page_posts_create_post(self) -> None:
        """Тест URL 'posts:create_post'"""
        response = self.AUTHORIZED_CLIENT_1.get(reverse('posts:post_create'))
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
        response = self.AUTHORIZED_CLIENT_1.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewsTests.POST_ID}
            )
        )
        self.assertEqual(
            Post.objects.get(id=PostsViewsTests.POST_ID).text,
            response.context['post'].text
        )
        self.assertIsInstance(
            response.context['comments_form'].fields['text'],
            fields.CharField)

    def test_page_post_post_edit(self) -> None:
        """Тест URL 'post:post_edit'"""
        response = self.AUTHORIZED_CLIENT_1.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewsTests.POST_ID}
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
            'post_id': PostsViewsTests.POST_ID,
        }
        for value, expected in test_dict.items():
            response_value = response.context[value]
            with self.subTest(value=value):
                self.assertEqual(response_value, expected)

    def test_page_post_profile(self) -> None:
        """Тест URL 'post:profile'"""
        response = self.AUTHORIZED_CLIENT_1.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.USER_1}
            )
        )
        response_value = str(response.context['author'])
        self.assertEqual(response_value, str(PostsViewsTests.USER_1))

    def test_subscriptions(self):
        """Тест подписок на авторов"""
        Post.objects.create(
            author=PostsViewsTests.USER_2,
            text='Пост для теста подписки',
        )
        follow_post = Post.objects.get(id=PostsViewsTests.POST_ID + 1)
        response = PostsViewsTests.GUEST_CLIENT.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        subscriptions = {
            PostsViewsTests.GUEST_CLIENT: [PostsViewsTests.USER_1, 0],
            PostsViewsTests.AUTHORIZED_CLIENT_1: [PostsViewsTests.USER_1, 0],
            PostsViewsTests.AUTHORIZED_CLIENT_1: [PostsViewsTests.USER_2, 1],
        }
        for user, result in subscriptions.items():
            with self.subTest(field=user):
                user.get(
                    f'/profile/{result[0]}/follow/'
                )
                self.assertEqual(Follow.objects.count(), result[1])
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:follow_index')
        )
        len_context = len(response.context['page_obj'])
        self.assertEqual(len_context, 1)
        self.assertEqual(
            str(response.context['page_obj'][:len_context][0]),
            str(follow_post)
        )
        PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            f'/profile/{PostsViewsTests.USER_2}/unfollow/'
        )
        self.assertEqual(Follow.objects.count(), 0)
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        follow_post.delete()

    def test_paginator(self) -> None:
        """Тест paginator для 'posts:index/profile/group_list'"""
        test_dict_count_2 = {
            1: PAGE_POST_COUNT,
            2: ONE_MORE_PAGE_POST_COUNT,
        }
        test_dict_count_3 = {
            1: PAGE_POST_COUNT,
            2: PAGE_POST_COUNT,
            3: (ONE_MORE_PAGE_POST_COUNT * DIFFERENT_GROUPS_COUNT),
        }
        group_list_reverse = reverse(
            'posts:group_list',
            kwargs={'group': PostsViewsTests.SLUG}
        )
        test_dict_reverse = {
            reverse('posts:index'): test_dict_count_3,
            reverse(
                'posts:profile',
                kwargs={'username': str(PostsViewsTests.USER_1)}
            ): test_dict_count_3,
            group_list_reverse: test_dict_count_2,
        }
        for path, count in test_dict_reverse.items():
            for field, expected in count.items():
                with self.subTest(field=field):
                    start_index: int = 0
                    end_index: int = 0
                    if field == 1:
                        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
                            path
                        )
                        end_index = expected
                    if field > 1:
                        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
                            path + f'?page={field}'
                        )
                        start_index = (field - 1) * PAGE_POST_COUNT
                        end_index = start_index + expected
                    response_value = len(response.context['page_obj'])
                    self.assertEqual(response_value, expected)
                    response_value = list(response.context['page_obj'])
                    cache.clear()
                    if group_list_reverse == path:
                        expected = list(
                            Post.objects.filter(
                                group=PostsViewsTests.GROUP
                            )[start_index:end_index]
                        )
                    else:
                        expected = list(
                            Post.objects.all()[start_index:end_index]
                        )
                    self.assertEqual(response_value, expected)

    def test_cache_for_index(self) -> None:
        """Тест cache для страницы 'posts:index'"""
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:index')
        )
        old_content = response.content
        new_post_data = {'text': 'Пост для тестирования cache'}
        PostsViewsTests.AUTHORIZED_CLIENT_1.post(
            reverse('posts:post_create'),
            data=new_post_data,
        )
        new_post_id = Post.objects.latest('id').id
        self.assertEqual(new_post_id, PostsViewsTests.POST_ID + 1)
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:index')
        )
        cached_content = response.content
        Post.objects.filter(id=new_post_id).delete()
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:index')
        )
        new_content = response.content
        self.assertEqual(new_content, cached_content)
        cache.clear()
        response = PostsViewsTests.AUTHORIZED_CLIENT_1.get(
            reverse('posts:index')
        )
        uncached_content = response.content
        self.assertEqual(uncached_content, old_content)
