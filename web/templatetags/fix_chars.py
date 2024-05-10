from django import template

register = template.Library()

@register.filter(name='fix_chars')
def fix_chars(value):
    return value.replace("&apos;", "'")