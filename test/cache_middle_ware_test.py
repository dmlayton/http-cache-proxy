import unittest
from mockito import mock, when, verify, never
from mockito import any as Any
from webob import Request, Response
from http_cache.cache_middle_ware import CacheMiddleWare


class TestsCacheMiddleWare(unittest.TestCase):
    def setUp(self):
        self.app = mock()
        self.cache = mock()
        self.wrapped = CacheMiddleWare(self.app, self.cache)
        self.environ = {'REQUEST_METHOD': 'GET',
                       'SCRIPT_NAME': '',
                       'PATH_INFO':'/service',
                       'QUERY_STRING':'a=1',
                       'SERVER_NAME': "www.test.com",
                       'SERVER_PORT': "8080",
                       'SERVER_PROTOCOL': "HTTP/1.0",
                       'wsgi.version': (1, 0),
                       'wsgi.url_scheme': 'http'}

    def _set_uncached_response(self, status, headers):
        request = Request(self.environ)
        response = Response('response_body_new', status, headers)
        when(request).get_response(self.app).thenReturn(response)
        when(self.cache).get('/service?a=1').thenReturn(None)
        return request, response,  self.wrapped.get_response(request)

    def test_call(self):
        response = mock()
        response.status = '200 OK'
        response.headerlist = [('header', 'value')]
        response.app_iter = ["1", "2", "3"]
        when(self.wrapped).get_response(Any(Request)).thenReturn(response)
        start = []
        def start_response(status, headers):
            return start.append((status, headers))

        result = self.wrapped(self.environ, start_response)
        self.assertIs(response.app_iter, result)
        self.assertEqual([(response.status, response.headerlist)], start)

    def test_get_response_returns_cached_response(self):
        request = Request(self.environ)
        metadata = {'response_body': 'response_body_cached', 'status': '200 OK',
                    'response_headers': [('cache-control', 'public; max-age=10')]}
        response = Response('response_body_new', '200 OK', [('cache-control', 'public; max-age=10')])
        when(request).get_response(self.app).thenReturn(response)
        when(self.cache).get('/service?a=1').thenReturn(metadata)
        result = self.wrapped.get_response(request)
        self.assertIs(result.body, metadata['response_body'])
        self.assertIs(result.status, metadata['status'])
        self.assertIs(result.headerlist, metadata['response_headers'])

    def test_get_response_returns_new_response_if_request_not_cacheable(self):
        self.environ['REQUEST_METHOD'] = 'DELETE'
        request = Request(self.environ)
        metadata = {'response_body': 'response_body_cached', 'status': '200 OK',
                    'response_headers': [('cache-control', 'public; max-age=10')]}
        response = Response('response_body_new', '200 OK',
                            [('cache-control', 'public; max-age=10')])
        when(request).get_response(self.app).thenReturn(response)
        when(self.cache).get('/service?a=1').thenReturn(metadata)
        result = self.wrapped.get_response(request)
        self.assertIs(response, result)

    def test_get_response_returns_new_response_of_cached_missed(self):
        request, response, result = self._set_uncached_response('200 OK', [('cache-control', 'public; max-age=10')])
        self.assertIs(response, result)

    def test_get_response_caches_new_response_if_appropriate(self):
        request, response, result = self._set_uncached_response('200 OK', [('cache-control', 'public; max-age=10')])
        verify(self.cache).set('/service?a=1', response.status, response.headerlist, response.body, 10)

    def test_get_response_does_not_cache_response_if_inappropriate(self):
        self._set_uncached_response('503 SERVICE UNAVAILABLE', [('cache-control', 'public; max-age=10')])
        verify(self.cache, never).set(Any(str), Any(str), Any(list), Any(str), Any(int))

    def test_get_response_honors_cache_control_no_cache(self):
        self._set_uncached_response('200 OK', [('cache-control', 'no-cache; max-age=10')])
        verify(self.cache, never).set(Any(str), Any(str), Any(list), Any(str), Any(int))

    def test_get_response_does_not_cache_if_no_ttl(self):
        self._set_uncached_response('200 OK', [('cache-control', 'public')])
        verify(self.cache, never).set(Any(str), Any(str), Any(list), Any(str), Any(int))

    def test_get_response_caches_new_response_if_s_max_age(self):
        request, response, result = self._set_uncached_response('200 OK', [('cache-control', 'public; s-maxage=20')])
        verify(self.cache).set('/service?a=1', response.status, response.headerlist, response.body, 20)

    def test_get_response_caches_new_response_if_expires_in_future(self):
        request, response, result = self._set_uncached_response('200 OK', [('expires', 'Thu, 01 Dec 2044 16:00:00 GMT')])
        verify(self.cache).set('/service?a=1', response.status, response.headerlist, response.body, Any(int))

    def test_get_response_does_not_cache_if_expires_in_past(self):
        request, response, result = self._set_uncached_response('200 OK', [('expires', 'Thu, 01 Dec 2000 16:00:00 GMT')])
        verify(self.cache, never).set(Any(str), Any(str), Any(list), Any(str), Any(int))

