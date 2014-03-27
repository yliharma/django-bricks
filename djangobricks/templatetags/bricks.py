from django import template

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
    request = context.pop('request', None)
    if request is not None:
        context_instance = template.RequestContext(request)
    else:
        context_instance = template.Context()
    context_instance.update(brick.get_context())
    context_instance.update(extra_context)
    t = template.loader.get_template(brick.template_name)
    try:
        return t.render(context_instance)
    finally:
        context_instance.pop()
