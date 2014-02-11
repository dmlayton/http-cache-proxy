from restkit.contrib.wsgi_proxy import Proxy
import logging

LOG = logging.getLogger(__name__)

class DynamicHostProxy(Proxy):

    """A proxy based on HTTP_HOST environ variable naming"""

    def extract_uri(self, environ):
        port = None
        scheme = environ['wsgi.url_scheme']
        host = environ['HTTP_HOST']
        if ':' in host:
            host, port = host.split(':')

        if not port:
            port = scheme == 'https' and '443' or '80'
        host = host.partition('.')[-1]
        environ['HTTP_HOST'] = '%s:%s' % (host, port) if ':' in environ['HTTP_HOST'] else host
        uri = '%s://%s:%s' % (scheme, host, port)
        LOG.info('using {}, {}'.format(environ['HTTP_HOST'], uri))
        return uri
