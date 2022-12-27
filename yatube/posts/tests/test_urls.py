from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from ..models import Comment
from ..models import Follow
from ..models import Group
from ..models import Post


class PostsURLTests(TestCase):
    """Тестирование URL приложения 'posts'"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER = User.objects.create(username='Author')
        cls.USER_NON_AUTHOR = User.objects.create(username='NotAuthor')
        cls.group = Group.objects.create(
            description='Тестовое описание группы',
            slug='test_slug',
            title='Тестовое наименование группы',
        )
        cls.post = Post.objects.create(
            author=cls.USER,
            group=cls.group,
            text='Тестовый текст тестового поста, который более 5 слов',
        )
        cls.comment = Comment.objects.create(
            author=cls.USER,
            post=cls.post,
            text='Классный тестовый текст! И комментарий!!'
        )
        cls.follow = Follow.objects.create(
            user=cls.USER,
            author=cls.USER_NON_AUTHOR,
        )
        cls.GUEST_CLIENT = Client()
        cls.AUTHORIZED_CLIENT = Client()
        cls.AUTHORIZED_CLIENT.force_login(cls.USER)
        cls.AUTHORIZED_CLIENT_NON_AUTHOR = Client()
        cls.AUTHORIZED_CLIENT_NON_AUTHOR.force_login(cls.USER_NON_AUTHOR)
        cls.SLUG = cls.group.slug
        cls.ID = Post.objects.latest('id').id
        cls.test_dict_http = {
            '/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            f'/group/{cls.SLUG}/': HTTPStatus.OK,
            f'/posts/{cls.ID}/': HTTPStatus.OK,
            f'/posts/{cls.ID}/comment/': HTTPStatus.FOUND,
            f'/posts/{cls.ID}/edit/': HTTPStatus.OK,
            f'/profile/{cls.USER}/': HTTPStatus.OK,
            f'/profile/{cls.USER_NON_AUTHOR}/unfollow/': HTTPStatus.OK,
            f'/profile/{cls.USER_NON_AUTHOR}/follow/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        cls.test_dict_html = {
            '/': 'includes/posts/index.html',
            '/create/': 'includes/posts/create_post.html',
            '/follow/': 'includes/posts/follow.html',
            f'/group/{cls.SLUG}/': 'includes/posts/group_list.html',
            f'/posts/{cls.ID}/': 'includes/posts/post_detail.html',
            f'/posts/{cls.ID}/edit/': 'includes/posts/create_post.html',
            f'/profile/{cls.USER}/': 'includes/posts/profile.html',
            f'/profile/{cls.USER_NON_AUTHOR}/unfollow/': (
                'includes/posts/profile.html'
            ),
            f'/profile/{cls.USER_NON_AUTHOR}/follow/': (
                'includes/posts/profile.html'
            ),
        }
        cls.test_dict_guest_changes = [
            '/create/',
            '/follow/',
            f'/posts/{PostsURLTests.ID}/comment/',
            f'/posts/{PostsURLTests.ID}/edit/',
            f'/profile/{PostsURLTests.USER_NON_AUTHOR}/unfollow/',
            f'/profile/{PostsURLTests.USER_NON_AUTHOR}/follow/',
        ]

    def setUp(self):
        cache.clear()

    def test_guest_pages_access_code(self) -> None:
        """Тест доступа неавторизованного пользователя к сайту"""
        test_dict_http = PostsURLTests.test_dict_http
        for path in PostsURLTests.test_dict_guest_changes:
            test_dict_http[path] = HTTPStatus.FOUND
        for value, expected in test_dict_http.items():
            response = PostsURLTests.GUEST_CLIENT.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, expected)

    def test_authorized_client_pages_access_code(self) -> None:
        """Тест доступа авторизованного пользователя к сайту"""
        for value, expected in PostsURLTests.test_dict_http.items():
            response = PostsURLTests.AUTHORIZED_CLIENT.get(value)
            with self.subTest(item=value):
                self.assertEqual(response.status_code, expected)

    def test_authorized_non_author_client_post_edit_code(self) -> None:
        """Тест доступа пользователя к редактированию не своего поста"""
        status = HTTPStatus.FOUND
        response = PostsURLTests.AUTHORIZED_CLIENT_NON_AUTHOR.get(
            reverse('posts:post_edit', kwargs={'post_id': PostsURLTests.ID})
        )
        self.assertEqual(response.status_code, status)

    def test_guest_pages_access_template(self) -> None:
        """Тест шаблонов для неавторизованного пользователя"""
        test_dict_html = PostsURLTests.test_dict_html
        for path in PostsURLTests.test_dict_guest_changes:
            test_dict_html[path] = 'includes/users/login.html'
        for value, expected in test_dict_html.items():
            response = PostsURLTests.GUEST_CLIENT.get(value, follow=True)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)
        test_dict_redirect = {}
        for path in PostsURLTests.test_dict_guest_changes:
            test_dict_redirect[path] = f'/auth/login/?next={path}'
        for value, expected in test_dict_redirect.items():
            response = self.GUEST_CLIENT.get(value, follow=True)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)

    def test_authorized_client_pages_access_template(self) -> None:
        """Тест шаблонов для авторизованного пользователя"""
        for value, expected in PostsURLTests.test_dict_html.items():
            response = PostsURLTests.AUTHORIZED_CLIENT.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_non_author_client_pages_access_template(self) -> None:
        """Тест шаблона пользователя для редактированию не своего поста"""
        template = 'includes/posts/post_detail.html'
        response = PostsURLTests.AUTHORIZED_CLIENT_NON_AUTHOR.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLTests.ID}
            ),
            follow=True
        )
        self.assertTemplateUsed(response, template)
