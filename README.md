http-cache-proxy
================
WSGI middleware to add HTTP Caching 
usage
================
You can create a standalone deployable wsgi app, by wrapping a proxy app like so 
```python
from restkit.contrib.wsgi_proxy import Proxy
from redis.client import StrictRedis
from http_cache import RedisCache, CacheMiddleWare

proxy = Proxy(strip_script_name=True)
app = CacheMiddleWare(proxy, RedisCache(StrictRedis())
```
or if you just what to add http caching to your own app
```python
from my_mod import my_app
from redis.client import StrictRedis
from http_cache import RedisCache, CacheMiddleWare

app = CacheMiddleWare(my_app, RedisCache(StrictRedis())
```
You can also use your own cache (just define get and set)
```python
from my_mod import my_app, MyCache
from redis.client import StrictRedis
from http_cache import CacheMiddleWare

app = CacheMiddleWare(my_app, MyCache())
```
