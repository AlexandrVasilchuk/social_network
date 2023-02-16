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
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related(
                    'author',
                    'group',
                ),
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    return render(
        request,
        'posts/group_list.html',
        {
            'page_obj': paginate(
                request,
                get_object_or_404(Group, slug=slug).posts.select_related(
                    'author',
                    'group',
                ),
            ),
            'group': get_object_or_404(Group, slug=slug),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': paginate(
                request,
                get_object_or_404(
                    User,
                    username=username,
                ).posts.select_related(
                    'author',
                ),
            ),
            'author': get_object_or_404(User, username=username),
            'following': bool(
                request.user.is_authenticated
                and get_object_or_404(User, username=username)
                .following.filter(user=request.user)
                .exists(),
            ),
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:

    return render(
        request,
        'posts/post_detail.html',
        {
            'post': get_object_or_404(Post, pk=pk),
            'comments': get_object_or_404(Post, pk=pk).comments.select_related(
                'author',
            ),
            'form': CommentForm(
                request.POST or None,
            ),
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
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = get_object_or_404(Post, pk=pk)
        form.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.filter(
        author__following__user=request.user,
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
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    get_object_or_404(
        Follow.objects.filter(author__following__user=request.user),
        author=get_object_or_404(User, username=username),
    ).delete()
    return redirect('posts:follow_index')
