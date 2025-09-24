from django import template

register = template.Library()


@register.filter
def after_phrase(value: str, phrase: str):
    """
    Returns the substring of value starting at 'phrase' if present,
    else returns value unchanged.
    """
    if not value or not phrase:
        return value
    idx = value.find(phrase)
    return value[idx:] if idx != -1 else value
