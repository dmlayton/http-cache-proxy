import unittest
from mockito import when, mock, verify
from mockito import any as Any
from http_cache.redis_cache import RedisCache

PREFIX = "PREFIX."


class TestsRedisCache(unittest.TestCase):
    def setUp(self):
        self.client = mock()
        self.cache = RedisCache(self.client, PREFIX)
        self.pipe = mock()

    def test_set(self):
        expected_key = PREFIX + "key"
        when(self.client).pipeline().thenReturn(self.pipe)
        when(self.pipe).hmset(expected_key, Any(dict)).thenReturn(self.pipe)

        self.cache.set("key", "200 OK", [("header", "value")], ["Hello", "World"], ttl=20)
        verify(self.client).pipeline()
        cache_entry = {
            'status': "200 OK",
            'response_headers': '[["header", "value"]]',
            'response_body': 'HelloWorld',
            'etag': self.cache.etag_hash('HelloWorld'),
        }
        verify(self.pipe).expire(expected_key, 20)
        verify(self.pipe).hmset(expected_key, cache_entry)
        verify(self.pipe).execute()


    def test_get(self):
        expected_key = PREFIX + "key"
        cache_entry = {
            'status': "200 OK",
            'response_headers': '[["header", "value"]]',
            'response_body': 'HelloWorld',
        }
        when(self.client).hgetall(expected_key).thenReturn(cache_entry)
        result = self.cache.get("key")
        self.assertDictEqual(
            {'status': "200 OK",
            'response_headers': [["header", "value"]],
            'response_body': 'HelloWorld'},
             result
        )