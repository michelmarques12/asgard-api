import unittest
from unittest import mock

from redis.exceptions import ConnectionError

from hollowman import cache
from hollowman.app import application

cache.__cache_backend.init_app(application)

class CacheWrapperTest(unittest.TestCase):

    def setUp(self):
        self.logger_patcher = mock.patch.object(cache, 'logger')
        self.logger_mock = self.logger_patcher.start()

    def tearDown(self):
        self.logger_patcher.stop()

    def test_get_with_offline_cache_returns_None(self):
        """
        Caso o cache esteja fora do ar não lançamos exepction
        apenas retornamos None (como se a chave não estivesse no cache)
        e fazemos um logger.error() avisando que não conseguimos conecta no cache
        """
        self.assertIsNone(cache.get("some-key"))

    def test_get_with_offline_cache_check_logger(self):
        self.assertIsNone(cache.get("my-key"))
        self.assertEqual(self.logger_mock.error.call_count, 1)
        self.logger_mock.error.assert_called_with({"action": "cache-get", "state": "error", "key": "my-key", "cache-backend": "redis://127.0.0.1:6379/0"})

    def test_get_calls_backend_get_method(self):
        with mock.patch.object(cache, '__cache_backend') as cache_backend_mock:
            cache_backend_mock.get.return_value = "My-Key-Value"
            self.assertEqual("My-Key-Value", cache.get("my-key"))
            cache_backend_mock.get.assert_called_with("my-key")

    def test_set_with_offline_cache_returns_False(self):
        self.assertFalse(cache.set("my-key", "my-value"))

    def test_set_with_offline_cache_check_logger(self):
        self.assertFalse(cache.set("my-key", 10))
        self.assertEqual(self.logger_mock.error.call_count, 1)
        self.logger_mock.error.assert_called_with({"action": "cache-set", "state": "error", "key": "my-key", "cache-backend": "redis://127.0.0.1:6379/0"})

    def test_set_calls_backend_set_method(self):
        with mock.patch.object(cache, '__cache_backend') as cache_backend_mock:
            cache_backend_mock.set.return_value = True
            self.assertTrue(cache.set("my-key", "my-value", timeout=30))
            cache_backend_mock.set.assert_called_with("my-key", "my-value", timeout=30)

