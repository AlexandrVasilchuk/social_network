from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.select_related(
        'author',
        'group',
    )
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(request, posts),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related(
        'author',
        'group',
    )
    return render(
        request,
        'posts/group_list.html',
        {
            'page_obj': paginate(request, posts),
            'group': group,
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related(
        'author',
    )
    following = False
    if request.user.is_authenticated:
        author = get_object_or_404(User, username=username)
        if author.following.filter(user=request.user):
            following = True
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': paginate(request, posts),
            'author': user,
            'following': following,
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related(
        'author',
    )
    form = CommentForm(
        request.POST or None,
    )
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
            },
        )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, id=pk)
    if request.user != post.author:
        return redirect('posts:post_detail', pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'is_edit': True,
                'form': form,
            },
        )
    post.save()
    return redirect('posts:post_detail', pk)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    form = CommentForm(request.POST)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', pk=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related(
        'author',
        'group',
    )
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(request, posts),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str):
    Follow.objects.get_or_create(
        user=request.user, author=get_object_or_404(User, username=username)
    )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    Follow.objects.get(
        user=request.user, author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:follow_index')
