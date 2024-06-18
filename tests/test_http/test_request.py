import unittest
from io import BytesIO

from framework.http import env, query, cookie, form, upload
from framework.service import http, Service

from .. import DummyStartResponse

app, start_response = Service(__name__), DummyStartResponse()


class TestModule(unittest.TestCase):
    def test_env(self):
        environ = dict(PATH_INFO='', QUERY_STRING='')

        tuple(app(environ, start_response))

        self.assertEqual('', env('PATH_INFO'))
        self.assertEqual('', env('QUERY_STRING'))

        environ['PATH_INFO'] = '/path.info'
        environ['QUERY_STRING'] = 'query=string'

        tuple(app(environ, start_response))

        self.assertEqual('/path.info', env('PATH_INFO'))
        self.assertEqual('query=string', env('QUERY_STRING'))

    def test_query(self):
        environ = dict(QUERY_STRING='')

        tuple(app(environ, start_response))

        self.assertDictEqual({}, http.call.query)

        environ['QUERY_STRING'] = 'query'

        tuple(app(environ, start_response))

        self.assertEqual('', query('query'))

        environ['QUERY_STRING'] = 'one=one%20query&two=two%20query'

        tuple(app(environ, start_response))

        self.assertEqual('one query', query('one'))
        self.assertEqual('two query', query('two'))

    def test_cookie(self):
        environ = dict(QUERY_STRING='')

        tuple(app(environ, start_response))

        self.assertDictEqual({}, http.call.cookie)

        environ['HTTP_COOKIE'] = 'one=one cookie; two=two cookie'

        tuple(app(environ, start_response))

        self.assertEqual('one cookie', cookie('one'))
        self.assertEqual('two cookie', cookie('two'))

    def test_form(self):
        environ = dict(QUERY_STRING='')

        tuple(app(environ, start_response))

        self.assertDictEqual({}, http.call.form.data)
        self.assertDictEqual({}, http.call.form.upload)

        environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        environ['wsgi.input'] = BytesIO(b'one=one form&two=two form')

        tuple(app(environ, start_response))

        self.assertEqual('one form', form('one'))
        self.assertEqual('two form', form('two'))
        self.assertDictEqual({}, http.call.form.upload)

        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=----TestBoundarySeparator'
        environ['wsgi.input'] = BytesIO(
            b'------TestBoundarySeparator\r\n'
            b'Content-Disposition: form-data; name="one"\r\n'
            b'\r\n'
            b'one input\r\n'
            b'------TestBoundarySeparator\r\n'
            b'Content-Disposition: form-data; name="two"\r\n'
            b'\r\n'
            b'two input\r\n'
            b'------TestBoundarySeparator\r\n'
            b'Content-Disposition: form-data; name="files"; filename="file.txt"\r\n'
            b'Content-Type: text/plain\r\n'
            b'\r\n'
            b'simple text\r\n'
            b'*\r\n'
            b'simple text\r\n'
            b'------TestBoundarySeparator--\r\n'
        )

        tuple(app(environ, start_response))

        self.assertEqual('one input', form('one'))
        self.assertEqual('two input', form('two'))
        self.assertDictEqual(
            {'file.txt': {'body': b'simple text\r\n*\r\nsimple text', 'type': 'text/plain'}},
            upload('files')
        )


def request_tests():
    suite = unittest.TestSuite()

    for test in (
            'test_env',
            'test_query',
            'test_cookie',
            'test_form',
    ):
        suite.addTest(TestModule(test))

    return suite
