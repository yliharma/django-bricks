from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag(takes_context=True)
def render_brick(context, brick, **extra_context):
    """
    Shortcut to render a single brick.
    If `django.core.context_processors.request` is in your
    `TEMPLATE_CONTEXT_PROCESSORS`, the brick will render a `RequestContext`
    instance, otherwise it will default to `Context`.
    The method accepts keyword arguments that will be passed as extra context
    to the brick.
    """
    request = context.get('request')

    if request is not None:
        context_instance = template.RequestContext(request)
    else:
        context_instance = None

    dictionary = brick.get_context()
    dictionary.update(extra_context)
    return render_to_string(brick.template_name, dictionary, context_instance)
