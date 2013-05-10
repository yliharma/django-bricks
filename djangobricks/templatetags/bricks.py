from django import template

register = template.Library()

@register.simple_tag
def render_brick(brick, **extra_context):
    """
    Shortcut to render a single brick.
    It's possible to inject arguments in the context through extra_context.
    """
    return brick.render(**extra_context)