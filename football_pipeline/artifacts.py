"""Small JSON helpers; explicit new artifacts do not overwrite earlier records."""
import json
import os
from pathlib import Path
import tempfile


def read_json(path):
    def invalid(value):
        raise ValueError('non-finite JSON number: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=invalid)


def save_json(path, value):
    path = Path(path)
    text = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if path.exists():
        if read_json(path) == value:
            return path
        raise ValueError(f'{path} already exists with different content; choose a new artifact path')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, encoding='utf-8', delete=False) as f:
            temporary = Path(f.name)
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink()
    return path
