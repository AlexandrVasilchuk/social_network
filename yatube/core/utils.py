from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: str,
    pagesize: int = settings.PAGE_SIZE,
) -> str:
    paginator = Paginator(queryset, pagesize)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
