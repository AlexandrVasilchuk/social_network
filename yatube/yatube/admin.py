from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
