from datetime import datetime
from webob import Request, Response
import logging

METHODS = {'GET'}
STATUS_CODES = {200, 203, 204, 205, 300, 301, 410}
KEY_TEMPLATE = '{req.path_info}?{req.query_string}'
DEFAULT_TTL = 0

LOG = logging.getLogger(__name__)

class CacheMiddleWare(object):
    def __init__(self, app, cache_store):
        self.app = app
        self.cache = cache_store
        LOG.info('CacheMiddleWare initialized.')

    def is_cacheable_request(self, request):
        return request.method in METHODS

    def get_cache_key(self, request):
        return KEY_TEMPLATE.format(req=request)

    def get_ttl(self, response):
        if response.cache_control.s_max_age is not None:
            return response.cache_control.s_max_age
        if response.cache_control.max_age is not None:
            return response.cache_control.max_age
        if response.expires:
            ttl = (response.expires.replace(tzinfo=None) - datetime.utcnow()).total_seconds()
            return int(ttl) if ttl > 0 else 0
        return DEFAULT_TTL

    def is_cacheable_response(self, response):
        cc = response.cache_control
        if cc.private or cc.no_store or cc.no_cache or cc.must_revalidate or cc.proxy_revalidate:
            return False
        return response.status_code in STATUS_CODES

    def _set(self, key, response, ttl):
        self.cache.set(key, response.status, response.headerlist, response.body, ttl)

    def _get(self, key):
        metadata = self.cache.get(key)
        if metadata is None:
            return None
        return Response(metadata['response_body'], metadata['status'], metadata['response_headers'])

    def _cache_response_if_appropriate(self, cache_key, response):
        if self.is_cacheable_response(response):
            ttl = self.get_ttl(response)
            if ttl:
                self._set(cache_key, response, ttl)

    def get_response(self, request):
        if request.content_length < 0:
            request.content_length = 0
        cache_key = self.get_cache_key(request)
        if not self.is_cacheable_request(request):
            response = request.get_response(self.app)
        else:
            response = None #self._get(cache_key)
            if response is None: #Response not cached
                response = request.get_response(self.app) #TODO: this should not block
                #self._cache_response_if_appropriate(cache_key, response)
            response = self._get(cache_key)
            if response is None: #Response not cached 
                response = request.get_response(self.app)
                self._cache_response_if_appropriate(cache_key, response)
        return response

    def __call__(self, environ, start_response):
        def start_response_from_response(response):
            start_response(response.status, response.headerlist)
            return response.app_iter
        LOG.debug(environ)
        request = Request(environ)
        response = self.get_response(request)
        return start_response_from_response(response)

