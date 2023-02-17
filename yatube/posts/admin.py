from django.contrib import admin

from posts.models import Comment, Follow, Group, Post
from yatube.admin import BaseAdmin


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)


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
        'created',
        'author',
    )


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'user',
        'author',
    )
