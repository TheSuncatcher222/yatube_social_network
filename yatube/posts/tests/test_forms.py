import shutil
import tempfile
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from posts.forms import PostForm
from posts.models import Comment
from posts.models import Follow
from posts.models import Group
from posts.models import Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.USER_1 = User.objects.create(username='test_user_1')
        cls.USER_2 = User.objects.create(username='test_user_2')
        cls.GUEST_CLIENT = Client()
        cls.AUTHORIZED_CLIENT_1 = Client()
        cls.AUTHORIZED_CLIENT_1.force_login(cls.USER_1)
        cls.AUTHORIZED_CLIENT_2 = Client()
        cls.AUTHORIZED_CLIENT_2.force_login(cls.USER_2)
        cls.GROUP_1 = Group.objects.create(
            description='Тестовое описание группы_1',
            slug='test_slug_1',
            title='Test group #1',
        )
        cls.POST_1 = Post.objects.create(
            author=cls.USER_1,
            group=cls.GROUP_1,
            text='Текст #1',
        )
        cls.POST_2 = Post.objects.create(
            author=cls.USER_2,
            text='Текст #2',
        )
        cls.form = PostForm()
        cls.post_first_count = Post.objects.count()
        cls.posts_last_id = Post.objects.last().id

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self) -> None:
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        new_post_data = {
            'text': 'Какой-то текст, да',
            'group': PostFormTest.GROUP_1.id,
            'image': uploaded,
        }
        response = PostFormTest.AUTHORIZED_CLIENT_1.post(
            reverse('posts:post_create'),
            data=new_post_data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.count(),
            PostFormTest.post_first_count + 1
        )
        post_current_count = Post.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_post = Post.objects.latest('id')
        self.assertEqual(new_post.text, new_post_data['text'])
        test_list = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'group': PostFormTest.GROUP_1.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTest.USER_1}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': new_post.id}
            ),
        ]
        for item in test_list:
            response = PostFormTest.AUTHORIZED_CLIENT_1.get(item)
            new_post_text = response.context['page_obj'][0].text
            self.assertEqual(new_post_text, new_post_data['text'])
            new_post_image = response.context['page_obj'][0].image
            self.assertTrue(new_post_image)
        response = PostFormTest.GUEST_CLIENT.post(
            reverse('posts:post_create'),
            data=new_post_data,
        )
        self.assertEqual(Post.objects.count(), post_current_count)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post(self) -> None:
        old_post = Post.objects.get(id=PostFormTest.posts_last_id)
        edit_post_data = {
            'text': 'Какой-то НОВЫЙ текст, да'
        }
        response = PostFormTest.GUEST_CLIENT.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTest.posts_last_id}
            ),
            data=edit_post_data,
        )
        self.assertEqual(
            old_post,
            Post.objects.get(id=PostFormTest.posts_last_id)
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        PostFormTest.AUTHORIZED_CLIENT_1.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTest.posts_last_id}
            ),
            data=edit_post_data,
            follow=True,
        )
        self.assertNotEqual(
            old_post,
            Post.objects.filter(id=PostFormTest.posts_last_id)
        )
        self.assertEqual(PostFormTest.post_first_count, Post.objects.count())

    def test_delete_post(self):
        new_post_data = {'text': 'Пост для тестирования удаления'}
        PostFormTest.AUTHORIZED_CLIENT_1.post(
            reverse('posts:post_create'),
            data = new_post_data,
        )
        post_new_count = Post.objects.count()
        post_new_id = Post.objects.last().id
        self.assertEqual(post_new_count, PostFormTest.post_first_count + 1)
        test_dict = {
            PostFormTest.GUEST_CLIENT: post_new_count,
            PostFormTest.AUTHORIZED_CLIENT_2: post_new_count,
            PostFormTest.AUTHORIZED_CLIENT_1: PostFormTest.post_first_count,
        }
        for client, posts_count in test_dict.items():
            with self.subTest(field=client):
                client.get(
                    reverse(
                        'posts:post_delete',
                        kwargs={'post_id': post_new_id}
                    ),
                )
                self.assertEqual(Post.objects.count(), posts_count)

    def test_create_comment(self):
        comments_init_count = Comment.objects.count()
        new_comment_data = {'text': 'Какой классный пост! И комментарий!'}
        response = PostFormTest.GUEST_CLIENT.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostFormTest.posts_last_id},
            ),
            data=new_comment_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Comment.objects.count(), comments_init_count)
        response = PostFormTest.AUTHORIZED_CLIENT_1.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostFormTest.posts_last_id},
            ),
            data=new_comment_data,
            follow=True,
        )
        new_comment_id = Comment.objects.last().id
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_init_count + 1)
        users_list: list[Client] = [
            PostFormTest.GUEST_CLIENT,
            PostFormTest.AUTHORIZED_CLIENT_1,
            PostFormTest.AUTHORIZED_CLIENT_2,
        ]
        for user in users_list:
            response = user.get(
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': PostFormTest.posts_last_id},
                )
            )
            with self.subTest(field=user):
                self.assertEqual(
                    response.context['post'].comments.get(id=new_comment_id),
                    Comment.objects.get(id=new_comment_id)
                )

    def test_delete_comment(self):
        comments_init_count = Comment.objects.count()
        new_comment_data = {'text': 'Комментарий для тестирования удаления'}
        PostFormTest.AUTHORIZED_CLIENT_1.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostFormTest.posts_last_id},
            ),
            data=new_comment_data,
        )
        comment_new_count = Comment.objects.count()
        self.assertEqual(comment_new_count, comments_init_count + 1)
        comment_new_id = Comment.objects.last().id
        test_dict = {
            PostFormTest.GUEST_CLIENT: comment_new_id,
            PostFormTest.AUTHORIZED_CLIENT_2: comment_new_id,
            PostFormTest.AUTHORIZED_CLIENT_1: comments_init_count,
        }
        for client, comments_count in test_dict.items():
            with self.subTest(field=client):
                client.get(
                    reverse(
                        'posts:delete_comment',
                        kwargs={'comment_id': comment_new_id}
                    ),
                )
                self.assertEqual(Comment.objects.count(), comments_count)
