from django import template

register = template.Library()

@register.filter
def index(sequence, i):
    try:
        return sequence[i]
    except:
        return ''

from django import template

register = template.Library()

@register.filter
def cyclic_index(list_, index):
    if not list_:
        return ''
    return list_[index % len(list_)]
