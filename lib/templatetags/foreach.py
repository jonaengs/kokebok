from django import template

register = template.Library()


@register.filter
def get_attr(items, attr):
    return map(lambda x: x.__getattribute__(attr), items)
