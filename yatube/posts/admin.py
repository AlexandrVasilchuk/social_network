from django.contrib import admin

from posts.models import Comment, Follow, Group, Post
from yatube.admin import BaseAdmin


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = (
        'title',
        'description',
    )


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = (
        'post',
        'text',
        'pub_date',
        'author',
    )


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'user',
        'author',
    )
