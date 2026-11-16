"""Small JSON source cache with retrieval provenance and explicit cache misses."""
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TTL_SECONDS = {'matches': 60, 'teams': 1800, 'matchDetails': 21600, 'targetDetails': 60, 'odds': 60, 'lineups': 60}


def _utc(value):
    if value.tzinfo is None:
        raise ValueError('timestamp must be timezone-aware')
    return value.astimezone(timezone.utc)


class Cache:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        return self.directory / (hashlib.sha256(key.encode('utf-8')).hexdigest() + '.json')

    def get(self, key, resource, now=None):
        """Return (hit, value, retrievedAt); cached JSON null remains a hit."""
        now = _utc(now or datetime.now(timezone.utc))
        try:
            entry = json.loads(self._path(key).read_text(encoding='utf-8'))
            retrieved = _utc(datetime.fromisoformat(entry['retrievedAt'].replace('Z', '+00:00')))
            age = (now - retrieved).total_seconds()
            ttl = TTL_SECONDS.get(resource, 0)
            if entry['key'] != key or entry['resource'] != resource or age < 0 or age >= ttl:
                return False, None, None
            return True, entry['value'], entry['retrievedAt']
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return False, None, None

    def put(self, key, resource, value, retrieved_at=None):
        stamp = _utc(retrieved_at or datetime.now(timezone.utc)).isoformat().replace('+00:00', 'Z')
        entry = {'key': key, 'resource': resource, 'retrievedAt': stamp, 'value': value}
        fd, name = tempfile.mkstemp(dir=self.directory, prefix='.cache-')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, separators=(',', ':'))
            os.replace(name, self._path(key))
        finally:
            if os.path.exists(name):
                os.unlink(name)
        return stamp
