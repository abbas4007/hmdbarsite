from django import template

register = template.Library()

@register.filter
def filesizeformat(value):
    if value < 512000:
        value = value / 1024.0
        ext = 'KB'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'MB'
    else:
        value = value / 1073741824.0
        ext = 'GB'
    return f'{value:.2f} {ext}'


@register.filter(name='endswith')
def endswith(value, arg):
    return value.endswith(arg)