import os
import unittest

from framework.routing import Rule, Map
from framework.service import Service
from framework.service.template import Template
from framework.utils import utc


class TestModule(unittest.TestCase):
    def test_templates(self):
        Service(__name__)

        dirname = os.path.dirname(__file__)

        self.assertEqual(os.path.abspath(os.path.join(dirname, 'templates')), getattr(Template, 'templates'))

        template_folder = os.path.abspath(os.path.join(dirname, '../templates'))

        Service(__name__, template_folder=template_folder)

        self.assertEqual(template_folder, Template.templates)

    def test_template(self):
        Service(__name__)

        self.assertEqual(
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <meta charset="utf-8">\n'
            '    <title>Raw page</title>\n'
            '    <link rel="stylesheet" href="style.css">\n'
            '    <link rel="stylesheet" href="template/style.css">\n'
            '</head>\n'
            '<body>\n'
            '<div id="content">\n'
            '    <h1>Raw title</h1>\n'
            '    <p class="important">Welcome! Raw page.</p>\n'
            '</div>\n'
            '<div id="footer">\n'
            '    <p>Template &copy; Copyright.</p>\n'
            '</div>\n'
            '</body>\n'
            '</html>', Template('template.html').template
        )

    def test_rendering(self):
        Service(__name__, Map((
            Rule('/', 'index'),
            Rule('/query', 'query'),
            Rule('/page/<name>', 'page', {'name': (0, r'[a-z.]+')}),
        )))

        date, context = utc.now.strftime('%d.%m.%Y'), {
            'title': 'Replace page',
            'date': utc.now,
            'year': (year := utc.now.strftime('%Y')),
        }

        self.assertEqual(
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <meta charset="utf-8">\n'
            '    <title>Replace page</title>\n'
            '    <link rel="stylesheet" href="/style.css">\n'
            '    <link rel="stylesheet" href="/replace.css">\n'
            '</head>\n'
            '<body>\n'
            '<div id="content">\n'
            '    <h1>Replace title %s</h1>\n'
            '    <ul class="menu">\n'
            '        <li><a href="/">Homepage</a></li>\n'
            '        <li><a href="/query?query">Query page</a></li>\n'
            '        <li><a href="/query?one=one value&two=two value">Query params</a></li>\n'
            '        <li><a href="/page/test.html">Page test</a></li>\n'
            '        <li><a href="/page/query.html?query=value">Page query</a></li>\n'
            '    </ul>\n'
            '</div>\n'
            '<div id="footer">\n'
            '    <p>Template &copy; Copyright %s.</p>\n'
            '</div>\n'
            '</body>\n'
            '</html>' % (date, year), Template('rendering.html').rendering(context)
        )


def template_tests():
    suite = unittest.TestSuite()

    for test in (
            'test_templates',
            'test_template',
            'test_rendering',
    ):
        suite.addTest(TestModule(test))

    return suite
