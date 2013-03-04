from django import template

register = template.Library()

@register.simple_tag
def render_brick(brick):
    """Shortcut to render a single brick."""
    return brick.render()