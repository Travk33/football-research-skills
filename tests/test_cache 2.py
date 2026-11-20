import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from football_pipeline.cache import Cache


class CacheTests(unittest.TestCase):
    def test_cached_null_and_ttl(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Cache(directory)
            now = datetime(2026, 1, 1, tzinfo=timezone.utc)
            cache.put('url', 'matches', None, now)
            self.assertEqual(cache.get('url', 'matches', now + timedelta(seconds=59))[:2], (True, None))
            self.assertEqual(cache.get('url', 'matches', now + timedelta(seconds=60))[:2], (False, None))
            self.assertFalse(cache.get('url', 'matches', now - timedelta(seconds=1))[0])
            self.assertFalse(cache.get('url', 'teams', now)[0])

    def test_resource_ttls_differ(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Cache(directory)
            now = datetime(2026, 1, 1, tzinfo=timezone.utc)
            cache.put('one', 'teams', {}, now)
            cache.put('two', 'odds', {}, now)
            self.assertTrue(cache.get('one', 'teams', now + timedelta(seconds=120))[0])
            self.assertFalse(cache.get('two', 'odds', now + timedelta(seconds=120))[0])
