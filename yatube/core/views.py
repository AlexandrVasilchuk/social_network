from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render


def page_not_found(
    request: HttpRequest, exception: HttpResponseNotFound,
) -> HttpResponse:
    del exception
    return render(
        request,
        'core/404.html',
        {
            'path': request.path,
        },
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    del reason
    return render(request, 'core/403csrf.html', status=HTTPStatus.FORBIDDEN)
