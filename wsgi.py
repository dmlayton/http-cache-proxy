import logging

logging.basicConfig()
LOG = logging.getLogger()
LOG.level = logging.DEBUG

from redis.client import StrictRedis
from http_cache import RedisCache, CacheMiddleWare

from http_cache.proxy import DynamicHostProxy

proxy = DynamicHostProxy(strip_script_name=False)
application = CacheMiddleWare(proxy, RedisCache(StrictRedis()))
