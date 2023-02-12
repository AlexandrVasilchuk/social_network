from django import template

register = template.Library()


@register.filter
def addclass(field, css: str) -> str:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
