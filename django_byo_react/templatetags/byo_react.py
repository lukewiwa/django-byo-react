from uuid import uuid4

from django import template

register = template.Library()


@register.inclusion_tag("django_byo_react/includes/byo_react.html")
def byo_react(id=uuid4(), component_name=None, className="", **kwargs):
    script_id = uuid4()
    return {
        "component_name": component_name,
        "element_id": id,
        "script_id": script_id,
        "className": className.strip(),
        "props": kwargs,
    }
