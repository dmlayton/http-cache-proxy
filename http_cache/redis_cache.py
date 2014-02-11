import hashlib
from json import loads, dumps

class RedisCache(object):
    def __init__(self, client, key_prefix='rc.'):
        self.client = client
        self.key_prefix = key_prefix

    def _set(self, cache_entry, key, ttl):
        redis_key = self._key(key)
        pipe = self.client.pipeline().hmset(redis_key, cache_entry)
        if ttl > 0:
            pipe.expire(redis_key, ttl)
        pipe.execute()

    def set(self, key, status, response_headers, response_body, ttl=-1):
        body = ''.join(response_body)
        etag = self.etag_hash(body)
        cache_entry = {
            'status': status,
            'response_headers': dumps(response_headers),
            'response_body': body,
            'etag': etag,
        }
        self._set(cache_entry, key, ttl)
        return etag

    def _load_headers(self, entry):
        entry['response_headers'] = loads(entry['response_headers'])

    def get(self, key):
        entry = self.client.hgetall(self._key(key))
        if entry:
            self._load_headers(entry)
        return entry or None

    def etag_hash(self, value):
        return hashlib.md5(value).hexdigest()

    def _key(self, key):
        return self.key_prefix + key
