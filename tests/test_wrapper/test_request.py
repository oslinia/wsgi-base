import unittest
from io import BytesIO

from framework.routing import Rule, Endpoint, Map, Path
from framework.service import http, Service
from framework.wrapper import Request

from .. import DummyStartResponse

start_response = DummyStartResponse()


class DummyMap(Request):
    def dummy_env(self):
        return str((self.env('PATH_INFO'), self.env('QUERY_STRING')))

    def dummy_not_found(self, code: int):
        return str((self.env('PATH_INFO'), self.env('QUERY_STRING'))), code

    def dummy_query(self, path: Path):
        if 'empty' == path['switch']:
            return str((self.query('query'),))

        if 'tuple' == path['switch']:
            return str((self.query('one'), self.query('two')))

        return str(http.call.query)

    def dummy_cookie(self, path: Path):
        if 'tuple' == path['switch']:
            return str((self.cookie('one'), self.cookie('two')))

        return str(http.call.cookie)

    def dummy_application(self, path: Path):
        if 'tuple' == path['switch']:
            return str((self.form('one'), self.form('two')))

        return str((http.call.form.data, http.call.form.upload))

    def dummy_multipart(self, path: Path):
        if 'tuple' == path['switch']:
            return str({
                'data': (self.form('one'), self.form('two')),
                'upload': self.upload('files'),
            })

        return str((http.call.form.data, http.call.form.upload))


class TestModule(unittest.TestCase):
    def test_env(self):
        app, environ = Service(__name__, Map((
            Rule('/env', 'env'),
            Endpoint('env', (DummyMap, 'dummy_env')),
        )), (DummyMap, 'dummy_not_found')), dict(PATH_INFO='', QUERY_STRING='')

        self.assertTupleEqual(('', ''), eval(b''.join(app(environ, start_response))))

        environ['PATH_INFO'] = '/path.info'
        environ['QUERY_STRING'] = 'query=string'

        self.assertTupleEqual(('/path.info', 'query=string'), eval(b''.join(app(environ, start_response))))

    def test_query(self):
        app, environ = Service(__name__, Map((
            Rule('/query/<switch>', 'query'),
            Endpoint('query', (DummyMap, 'dummy_query')),
        ))), dict(QUERY_STRING='')

        environ['PATH_INFO'] = '/query/request'

        self.assertDictEqual({}, eval(b''.join(app(environ, start_response))))

        environ['PATH_INFO'] = '/query/empty'
        environ['QUERY_STRING'] = 'query'

        self.assertTupleEqual(('',), eval(b''.join(app(environ, start_response))))

        environ['PATH_INFO'] = '/query/tuple'
        environ['QUERY_STRING'] = 'one=one%20query&two=two%20query'

        self.assertTupleEqual(('one query', 'two query'), eval(b''.join(app(environ, start_response))))

    def test_cookie(self):
        app, environ = Service(__name__, Map((
            Rule('/cookie/<switch>', 'cookie'),
            Endpoint('cookie', (DummyMap, 'dummy_cookie')),
        ))), dict(QUERY_STRING='')

        environ['PATH_INFO'] = '/cookie/request'

        self.assertDictEqual({}, eval(b''.join(app(environ, start_response))))

        environ['PATH_INFO'] = '/cookie/tuple'
        environ['HTTP_COOKIE'] = 'one=one cookie; two=two cookie'

        self.assertTupleEqual(('one cookie', 'two cookie'), eval(b''.join(app(environ, start_response))))

    def test_form(self):
        app, environ = Service(__name__, Map((
            Rule('/application/<switch>', 'application'),
            Endpoint('application', (DummyMap, 'dummy_application')),
            Rule('/multipart/<switch>', 'multipart'),
            Endpoint('multipart', (DummyMap, 'dummy_multipart')),
        ))), dict(QUERY_STRING='')

        environ['PATH_INFO'] = '/application/blank'

        self.assertTupleEqual(({}, {}), eval(b''.join(app(environ, start_response))))

        environ['PATH_INFO'] = '/application/tuple'
        environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        environ['wsgi.input'] = BytesIO(b'one=one application&two=two application')

        self.assertTupleEqual(
            ('one application', 'two application'),
            eval(b''.join(app(environ, start_response))),
        )

        environ = dict(QUERY_STRING='')

        environ['PATH_INFO'] = '/multipart/blank'

        self.assertTupleEqual(({}, {}), eval(b''.join(app(environ, start_response))))

        environ['PATH_INFO'] = '/multipart/tuple'
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
            b'------TestBoundarySeparator--\r\n'
        )

        self.assertDictEqual(
            {
                'data': ('one multipart', 'two multipart'),
                'upload': {'file.txt': {'type': 'text/plain', 'body': b'simple text'}},
            },
            eval(b''.join(app(environ, start_response))),
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
