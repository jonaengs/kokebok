from django import template

register = template.Library()


@register.filter
def get_attr(items, attr):
    return map(lambda x: x.__getattribute__(attr), items)


@register.filter
def sremove(items, value):
    return filter(lambda x: str(x) != value, items)
