from django import template

register = template.Library()

@register.filter
def index(sequence, position):
    """Return item at list index"""
    try:
        return sequence[int(position)]
    except (IndexError, ValueError, TypeError):
        return ''
