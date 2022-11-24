from unittest.mock import patch
from django.template import Context, Template
from django.test import TestCase

from django_byo_react.templatetags.byo_react import uuid


class ByoReactTestCase(TestCase):
    test_id = "test-id"

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_json_script_renders(self, mock_uuid):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react %}"""
        )
        self.assertInHTML(
            '<script id="two" type="application/json">{}</script>', rendered
        )

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

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_classname_renders(self, mock_uuid):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react className='w-100 h-100' %}""",
        )
        self.assertInHTML(
            '<div id="one" data-script-id="two" class="w-100 h-100"></div>', rendered
        )

    @patch.object(uuid, "uuid4", side_effect=["one", "two"])
    def test_uuid_id(self, mock_uuid):
        rendered = self.render_template(
            """{% load byo_react %}
            {% byo_react %}"""
        )
        self.assertInHTML(
            '<div id="one" data-script-id="two"></div>', rendered, msg_prefix=rendered
        )
