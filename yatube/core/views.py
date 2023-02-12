from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    del exception
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    return render(request, 'core/403csrf.html')
