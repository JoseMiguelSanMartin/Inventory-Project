from django import template

register = template.Library()


@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def percentage(have, required):
    try:
        have = int(have)
        required = int(required)

        if required <= 0:
            return 100

        return round((have / required) * 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0