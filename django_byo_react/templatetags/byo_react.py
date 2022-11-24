import uuid

from django import template

register = template.Library()


@register.inclusion_tag("django_byo_react/includes/byo_react.html")
def byo_react(id=None, component_name=None, className="", **kwargs):
    if id is None:
        id = uuid.uuid4()
    script_id = uuid.uuid4()
    return {
        "component_name": component_name,
        "element_id": id,
        "script_id": script_id,
        "className": className.strip(),
        "props": kwargs,
    }
