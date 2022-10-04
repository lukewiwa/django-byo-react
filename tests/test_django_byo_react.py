from django.template import Context, Template
from django.test import TestCase


class ByoReactTestCase(TestCase):
    test_id = "test-id"

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_json_script_passes_true_false(self):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react id=test_id true=True false=False %}""",
            context={"test_id": self.test_id},
        )
        self.assertInHTML('{"true": true, "false": false}', rendered)

    def test_json_script_passes_string(self):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react id=test_id string='string' %}""",
            context={"test_id": self.test_id},
        )
        self.assertInHTML('{"string": "string"}', rendered)

    def test_json_script_passes_dict(self):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react id=test_id testDict=test_dict %}""",
            context={"test_id": self.test_id, "test_dict": {"test": "test"}},
        )
        self.assertInHTML('{"testDict": {"test": "test"}}', rendered)

    def test_classname_renders(self):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react id=test_id className='w-100 h-100' %}""",
            context={"test_id": self.test_id},
        )
        self.assertIn('class="w-100 h-100"', rendered)
