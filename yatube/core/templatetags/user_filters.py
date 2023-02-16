from django import template
from django.forms.boundfield import BoundField

register = template.Library()


@register.filter
def addclass(field: BoundField, css: str) -> str:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
