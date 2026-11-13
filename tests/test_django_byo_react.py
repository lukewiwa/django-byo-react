from unittest.mock import patch

from django.template import Context, Template
from django.test import SimpleTestCase

from django_byo_react.templatetags.byo_react import uuid


def render(string, context=None):
    return Template("{% load byo_react %}" + string).render(Context(context or {}))


@patch.object(uuid, "uuid4", side_effect=["one", "two"])
class ByoReactMarkupTestCase(SimpleTestCase):
    """The rendered div/script pair, with UUIDs pinned."""

    def test_defaults(self, _):
        rendered = render("{% byo_react %}")
        self.assertInHTML(
            '<script id="two" type="application/json">{}</script>', rendered
        )
        self.assertInHTML('<div id="one" data-script-id="two"></div>', rendered)

    def test_classname(self, _):
        rendered = render("{% byo_react className='w-100 h-100' %}")
        self.assertInHTML(
            '<div id="one" data-script-id="two" class="w-100 h-100"></div>', rendered
        )

    def test_classname_is_stripped(self, _):
        rendered = render("{% byo_react className='  w-100  ' %}")
        self.assertInHTML(
            '<div id="one" data-script-id="two" class="w-100"></div>', rendered
        )

    def test_component_name(self, _):
        rendered = render("{% byo_react component_name='CounterField' %}")
        self.assertInHTML(
            '<div id="one" data-component-name="CounterField" data-script-id="two">'
            "</div>",
            rendered,
        )


@patch.object(uuid, "uuid4", side_effect=["script"])
class ByoReactIdTestCase(SimpleTestCase):
    """An explicit id skips the element UUID; the script always gets one."""

    def test_explicit_id(self, mock_uuid):
        rendered = render("{% byo_react id='react-app' %}")
        self.assertInHTML(
            '<div id="react-app" data-script-id="script"></div>', rendered
        )
        mock_uuid.assert_called_once()

    def test_id_from_context(self, _):
        rendered = render("{% byo_react id=app_id %}", {"app_id": "from-context"})
        self.assertInHTML(
            '<div id="from-context" data-script-id="script"></div>', rendered
        )

    def test_everything(self, _):
        rendered = render(
            "{% byo_react id='app' component_name='App' className='x' count=3 %}"
        )
        self.assertInHTML(
            '<script id="script" type="application/json">{"count": 3}</script>',
            rendered,
        )
        self.assertInHTML(
            '<div id="app" data-component-name="App" data-script-id="script" '
            'class="x"></div>',
            rendered,
        )


class ByoReactPropsTestCase(SimpleTestCase):
    """Extra kwargs end up as JSON props."""

    def test_bools(self):
        rendered = render("{% byo_react true=True false=False %}")
        self.assertInHTML('{"true": true, "false": false}', rendered)

    def test_none(self):
        rendered = render("{% byo_react nothing=None %}")
        self.assertInHTML('{"nothing": null}', rendered)

    def test_string(self):
        rendered = render("{% byo_react string='string' %}")
        self.assertInHTML('{"string": "string"}', rendered)

    def test_numbers(self):
        rendered = render("{% byo_react int=1 float=1.5 %}")
        self.assertInHTML('{"int": 1, "float": 1.5}', rendered)

    def test_dict(self):
        rendered = render("{% byo_react testDict=d %}", {"d": {"test": "test"}})
        self.assertInHTML('{"testDict": {"test": "test"}}', rendered)

    def test_list(self):
        rendered = render("{% byo_react items=items %}", {"items": [1, "two"]})
        self.assertInHTML('{"items": [1, "two"]}', rendered)

    def test_reserved_kwargs_are_not_props(self):
        rendered = render("{% byo_react id='a' component_name='B' className='c' %}")
        self.assertIn('type="application/json">{}</script>', rendered)

    def test_script_breakout_is_escaped(self):
        rendered = render(
            "{% byo_react evil=evil %}", {"evil": "</script><script>alert(1)"}
        )
        self.assertNotIn("</script><script>", rendered)
        self.assertIn("\\u003C/script\\u003E", rendered)

    def test_non_serialisable_prop_raises(self):
        with self.assertRaises(TypeError):
            render("{% byo_react thing=thing %}", {"thing": object()})
