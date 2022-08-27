from typing import AnyStr

from django import template

register = template.Library()


@register.inclusion_tag("django_byo_react/includes/byo_react.html")
def byo_react(id: AnyStr, className="", **kwargs):
    return {
        "element_id": id,
        "script_id": f"{id}-props",
        "className": className.strip(),
        "props": kwargs,
    }
