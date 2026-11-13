import json
import uuid as uuid_lib
from html.parser import HTMLParser
from unittest.mock import patch

from django.template import Context, Template
from django.test import SimpleTestCase

from django_byo_react.templatetags.byo_react import uuid


class ElementCollector(HTMLParser):
    """Collect top level elements as (tag, attrs, text) tuples."""

    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs), ""))

    def handle_data(self, data):
        if self.elements and data.strip():
            tag, attrs, text = self.elements[-1]
            self.elements[-1] = (tag, attrs, text + data)


class ByoReactTestCase(SimpleTestCase):
    test_id = "test-id"

    def render_template(self, string, context=None):
        return Template("{% load byo_react %}" + string).render(Context(context or {}))

    def parse(self, rendered):
        parser = ElementCollector()
        parser.feed(rendered)
        parser.close()
        return parser.elements

    def render_one(self, string, context=None):
        """Render a single tag and return its (script, div) elements."""
        elements = self.parse(self.render_template(string, context))
        self.assertEqual([tag for tag, _, _ in elements], ["script", "div"])
        (_, script_attrs, script_text), (_, div_attrs, _) = elements
        return script_attrs, json.loads(script_text), div_attrs

    def render_props(self, string, context=None):
        return self.render_one(string, context)[1]

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_default_render(self, mock_uuid):
        rendered = self.render_template("{% byo_react %}")
        self.assertHTMLEqual(
            rendered,
            '<script id="two" type="application/json">{}</script>'
            '<div id="one" data-script-id="two"></div>',
        )
        self.assertEqual(mock_uuid.call_count, 2)

    @patch.object(uuid, "uuid4", side_effect=["one"])
    def test_explicit_id(self, mock_uuid):
        rendered = self.render_template(
            "{% byo_react id=test_id %}", {"test_id": self.test_id}
        )
        self.assertHTMLEqual(
            rendered,
            '<script id="one" type="application/json">{}</script>'
            '<div id="test-id" data-script-id="one"></div>',
        )
        self.assertEqual(mock_uuid.call_count, 1)

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_component_name(self, mock_uuid):
        rendered = self.render_template("{% byo_react component_name='App' %}")
        self.assertHTMLEqual(
            rendered,
            '<script id="two" type="application/json">{}</script>'
            '<div id="one" data-script-id="two" data-component-name="App"></div>',
        )

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_all_arguments(self, mock_uuid):
        rendered = self.render_template(
            "{% byo_react id='app' component_name='App' className='w-100' a=1 %}"
        )
        self.assertHTMLEqual(
            rendered,
            '<script id="one" type="application/json">{"a": 1}</script>'
            '<div id="app" data-script-id="one" data-component-name="App"'
            ' class="w-100"></div>',
        )

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_classname_renders(self, mock_uuid):
        rendered = self.render_template("{% byo_react className='w-100 h-100' %}")
        self.assertInHTML(
            '<div id="one" data-script-id="two" class="w-100 h-100"></div>', rendered
        )

    def test_classname_is_stripped(self):
        _, _, div = self.render_one("{% byo_react className='  w-100 h-100  ' %}")
        self.assertEqual(div["class"], "w-100 h-100")

    def test_blank_classname_is_omitted(self):
        for class_name in ("", "   "):
            with self.subTest(class_name=class_name):
                _, _, div = self.render_one(
                    "{% byo_react className=class_name %}",
                    {"class_name": class_name},
                )
                self.assertNotIn("class", div)

    def test_reserved_arguments_are_not_props(self):
        props = self.render_props(
            "{% byo_react id='app' component_name='App' className='c' prop=1 %}"
        )
        self.assertEqual(props, {"prop": 1})

    def test_prop_types(self):
        cases = {
            "true": True,
            "false": False,
            "none": None,
            "string": "string",
            "empty_string": "",
            "int": 42,
            "negative": -1,
            "float": 1.5,
            "list": [1, "two", None],
            "dict": {"test": "test"},
            "nested": {"a": [{"b": {"c": [True]}}]},
            "unicode": "héllo ✓ 日本",
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                props = self.render_props(
                    "{% byo_react prop=value %}", {"value": value}
                )
                self.assertEqual(props, {"prop": value})

    def test_template_literal_props(self):
        props = self.render_props(
            "{% byo_react true=True false=False none=None string='s' int=3 %}"
        )
        self.assertEqual(
            props, {"true": True, "false": False, "none": None, "string": "s", "int": 3}
        )

    def test_prop_names_are_preserved(self):
        props = self.render_props("{% byo_react showActive=True snake_case=1 %}")
        self.assertEqual(props, {"showActive": True, "snake_case": 1})

    def test_props_cannot_break_out_of_script(self):
        payload = "</script><script>alert('xss')</script><!--"
        rendered = self.render_template(
            "{% byo_react prop=payload %}", {"payload": payload}
        )
        self.assertNotIn("</script><script>", rendered)
        self.assertEqual(rendered.count("</script>"), 1)
        _, props, _ = self.render_one(
            "{% byo_react prop=payload %}", {"payload": payload}
        )
        self.assertEqual(props, {"prop": payload})

    def test_attributes_are_escaped(self):
        payload = '"><script>alert(1)</script>'
        rendered = self.render_template(
            "{% byo_react id=payload component_name=payload className=payload %}",
            {"payload": payload},
        )
        self.assertNotIn("<script>alert", rendered)
        _, _, div = self.render_one(
            "{% byo_react id=payload component_name=payload className=payload %}",
            {"payload": payload},
        )
        self.assertEqual(div["id"], payload)
        self.assertEqual(div["data-component-name"], payload)
        self.assertEqual(div["class"], payload)

    def test_unserializable_prop_raises(self):
        with self.assertRaises(TypeError):
            self.render_template("{% byo_react prop=value %}", {"value": object()})

    def test_generated_ids_are_uuids(self):
        script, _, div = self.render_one("{% byo_react %}")
        uuid_lib.UUID(div["id"])
        uuid_lib.UUID(script["id"])
        self.assertNotEqual(div["id"], script["id"])

    def test_div_references_script(self):
        script, _, div = self.render_one("{% byo_react id='app' %}")
        self.assertEqual(script["type"], "application/json")
        self.assertEqual(div["data-script-id"], script["id"])

    def test_multiple_tags_have_unique_ids(self):
        rendered = self.render_template(
            "{% byo_react a=1 %}{% byo_react b=2 %}{% byo_react c=3 %}"
        )
        elements = self.parse(rendered)
        scripts = [e for e in elements if e[0] == "script"]
        divs = [e for e in elements if e[0] == "div"]
        self.assertEqual(len(scripts), 3)
        self.assertEqual(len(divs), 3)

        ids = [attrs["id"] for _, attrs, _ in elements]
        self.assertEqual(len(set(ids)), len(ids))

        scripts_by_id = {attrs["id"]: json.loads(text) for _, attrs, text in scripts}
        self.assertEqual(
            [scripts_by_id[attrs["data-script-id"]] for _, attrs, _ in divs],
            [{"a": 1}, {"b": 2}, {"c": 3}],
        )

    def test_same_component_name_rendered_repeatedly(self):
        rendered = self.render_template(
            "{% for value in values %}"
            "{% byo_react component_name='App' value=value %}"
            "{% endfor %}",
            {"values": [1, 2]},
        )
        elements = self.parse(rendered)
        divs = [attrs for tag, attrs, _ in elements if tag == "div"]
        self.assertEqual([d["data-component-name"] for d in divs], ["App", "App"])
        self.assertNotEqual(divs[0]["id"], divs[1]["id"])
        self.assertNotEqual(divs[0]["data-script-id"], divs[1]["data-script-id"])
