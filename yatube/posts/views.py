from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from core.constants import CACHE_TIME_SECONDS
from core.constants import PAGE_POST_COUNT
from .forms import CommentForm
from .forms import PostForm
from .models import Comment
from .models import Follow
from .models import Group
from .models import Post
from .models import User


def paginator_for_pages(objects_list, page_number):
    paginator = Paginator(objects_list, PAGE_POST_COUNT)
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(CACHE_TIME_SECONDS, key_prefix='index_page')
def index(request):
    """Отображает главную страницу сайта"""
    template = 'includes/posts/index.html'
    context = {
        'page_obj': paginator_for_pages(
            Post.objects.select_related('author', 'group'),
            request.GET.get('page')
        ),
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    """Отображает главную страницу сайта только с подписками пользователя"""
    template = 'includes/posts/follow.html'
    context = {
        'only_subscriptions': True,
        'page_obj': paginator_for_pages(
            Post.objects.select_related('author', 'group').filter(
                author__following__user=request.user
            ),
            request.GET.get('page'),
        ),
    }
    return render(request, template, context)


def groups(request, group):
    """Отображает страницу c постами запрошенной (group) группы"""
    group = get_object_or_404(Group, slug=str(group).lower())
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': paginator_for_pages(
            group.posts.select_related('author'),
            request.GET.get('page'),
        ),
    }
    return render(request, template, context)


def profile(request, username):
    """Отображает страницу c постами запрошенного (username) автора"""
    author = get_object_or_404(User, username=username)
    template = 'includes/posts/profile.html'
    following = False
    following_allow = False
    if request.user.is_authenticated:
        user = request.user
        if user != author:
            following_allow = True
            following = Follow.objects.filter(
                user=user,
                author=author
            ).exists()
    context = {
        'author': author,
        'page_obj': paginator_for_pages(
            author.posts.select_related('group'),
            request.GET.get('page'),
        ),
        'following': following,
        'following_allow': following_allow,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Создает подписку на автора"""
    author = User.objects.get(username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        if request.user != author:
            Follow.objects.create(
                user=request.user,
                author=author
            )
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    """Удаляет подписку на автора"""
    Follow.objects.get(
        user=request.user,
        author__username=username
    ).delete()
    return profile(request, username)


def post_detail(request, post_id):
    """Отображает страницу c запрошенным (post_id) постом"""
    post = get_object_or_404(Post, id=post_id)
    page_obj = Post.objects.filter(id=post_id)
    template = 'includes/posts/post_detail.html'
    context = {
        'comments_form': CommentForm(),
        'page_obj': page_obj,
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Отображает страницу для POST запроса на создание поста"""
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', username=request.user.username)
    form = PostForm()
    template = 'includes/posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Отображает страницу для POST запроса на изменение поста (post_id)"""
    edit_post = get_object_or_404(Post.objects, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=edit_post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    form = PostForm(instance=edit_post)
    template = 'includes/posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, template, context)


@login_required
def post_delete(request, post_id):
    """Тест удаления поста"""
    delete_post = Post.objects.get(id=post_id)
    if request.user == delete_post.author:
        delete_post.delete()
    return redirect('posts:index')


@login_required
def add_comment(request, post_id):
    """Тест добавления комментария"""
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def comment_delete(request, comment_id):
    """Тест удаления комментария"""
    delete_comment = Comment.objects.get(id=comment_id)
    post_id = Post.objects.get(comments=delete_comment).id
    if request.user == delete_comment.author:
        delete_comment.delete()
    return redirect('posts:post_detail', post_id=post_id)
