from datetime import date
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Добавляет переменную с текущим годом.

    Args:
        request: Любой запрос на сайт,
            что гарантирует выполнение функции во всех случаях.

    Returns:
        Словарь с ключом 'year'.
            Будем использовать ее в footer.
    """
    del request
    return {
        'year': date.today().year,
    }
