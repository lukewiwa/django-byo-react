from unittest.mock import patch

from django.template import Context, Template
from django.test import SimpleTestCase

TAG_UUID4 = "django_byo_react.templatetags.byo_react.uuid.uuid4"


@patch(TAG_UUID4, side_effect=["div-uuid", "script-uuid"])
class ByoReactTests(SimpleTestCase):
    def render(self, tag_args="", context=None):
        template = Template("{% load byo_react %}{% byo_react " + tag_args + " %}")
        return template.render(Context(context or {}))

    def test_defaults(self, _uuid4):
        rendered = self.render()
        self.assertHTMLEqual(
            rendered,
            '<script id="script-uuid" type="application/json">{}</script>'
            '<div id="div-uuid" data-script-id="script-uuid"></div>',
        )

    def test_explicit_id_skips_uuid(self, uuid4):
        rendered = self.render('id="react-app"')
        self.assertInHTML(
            '<div id="react-app" data-script-id="div-uuid"></div>', rendered
        )
        self.assertEqual(uuid4.call_count, 1)

    def test_component_name(self, _uuid4):
        rendered = self.render('component_name="App"')
        self.assertInHTML(
            '<div id="div-uuid" data-component-name="App"'
            ' data-script-id="script-uuid"></div>',
            rendered,
        )

    def test_class_name_is_stripped(self, _uuid4):
        rendered = self.render('className="  w-100 h-100 "')
        self.assertInHTML(
            '<div id="div-uuid" data-script-id="script-uuid" class="w-100 h-100">'
            "</div>",
            rendered,
        )

    def test_blank_class_name_omits_attribute(self, _uuid4):
        rendered = self.render('className="   "')
        self.assertInHTML(
            '<div id="div-uuid" data-script-id="script-uuid"></div>', rendered
        )

    def test_props(self, _uuid4):
        cases = [
            ("flag=True off=False", {}, '{"flag": true, "off": false}'),
            ("text='hello'", {}, '{"text": "hello"}'),
            ("count=3", {}, '{"count": 3}'),
            ("nothing=None", {}, '{"nothing": null}'),
            ("data=data", {"data": {"a": [1, 2]}}, '{"data": {"a": [1, 2]}}'),
        ]
        for tag_args, context, expected in cases:
            with self.subTest(tag_args), patch(TAG_UUID4, side_effect=["d", "s"]):
                rendered = self.render(tag_args, context)
                self.assertInHTML(
                    f'<script id="s" type="application/json">{expected}</script>',
                    rendered,
                )

    def test_props_are_escaped(self, _uuid4):
        rendered = self.render("evil=evil", {"evil": "</script><b>"})
        self.assertNotIn("</script><b>", rendered)
        self.assertIn("\\u003C/script\\u003E\\u003Cb\\u003E", rendered)
