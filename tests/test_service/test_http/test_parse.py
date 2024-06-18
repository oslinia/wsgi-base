import unittest
from io import BytesIO

from framework.service.http.parse import Query, Cookie, Form


class TestModule(unittest.TestCase):
    def test_query(self):
        environ = dict(QUERY_STRING='')

        self.assertDictEqual({}, Query(environ))

        environ['QUERY_STRING'] = 'one=one%20query&two=two%20query'

        self.assertDictEqual({'one': 'one query', 'two': 'two query'}, Query(environ))

    def test_cookie(self):
        environ = dict()

        self.assertDictEqual({}, Cookie(environ))

        environ['HTTP_COOKIE'] = 'one=one cookie; two=two cookie'

        self.assertDictEqual({'one': 'one cookie', 'two': 'two cookie'}, Cookie(environ))

    def test_form(self):
        environ = dict()

        form = Form(environ)

        self.assertDictEqual({}, form.data)
        self.assertDictEqual({}, form.upload)

        environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        environ['wsgi.input'] = BytesIO(b'one=one application&two=two application')

        form = Form(environ)

        self.assertDictEqual({'one': 'one application', 'two': 'two application'}, form.data)
        self.assertDictEqual({}, form.upload)

        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=----TestBoundarySeparator'
        environ['wsgi.input'] = BytesIO(
            b'------TestBoundarySeparator\r\n'
            b'Content-Disposition: form-data; name="one"\r\n'
            b'\r\n'
            b'one multipart\r\n'
            b'------TestBoundarySeparator\r\n'
            b'Content-Disposition: form-data; name="two"\r\n'
            b'\r\n'
            b'two multipart\r\n'
            b'------TestBoundarySeparator\r\n'
            b'Content-Disposition: form-data; name="files"; filename="file.txt"\r\n'
            b'Content-Type: text/plain\r\n'
            b'\r\n'
            b'simple text\r\n'
            b'*\r\n'
            b'simple text\r\n'
            b'------TestBoundarySeparator--\r\n'
        )

        form = Form(environ)

        self.assertDictEqual({'one': 'one multipart', 'two': 'two multipart'}, form.data)
        self.assertDictEqual(
            {'files': {
                'file.txt': {'body': b'simple text\r\n*\r\nsimple text', 'type': 'text/plain'}
            }}, form.upload)


def parse_tests():
    suite = unittest.TestSuite()

    for test in (
            'test_query',
            'test_cookie',
            'test_form',
    ):
        suite.addTest(TestModule(test))

    return suite
