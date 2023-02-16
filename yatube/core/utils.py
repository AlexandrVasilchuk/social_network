from typing import Any

from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    pagesize: int = settings.PAGE_SIZE,
) -> Page[Any]:
    return Paginator(
        queryset,
        pagesize,
    ).get_page(request.GET.get('page'))
