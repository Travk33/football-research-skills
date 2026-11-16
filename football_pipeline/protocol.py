"""Register prospective evaluation plans and preserve measurement snapshots."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile


CATEGORIES = frozenset({'wins-btts', 'other-markets', 'bet-builders'})
STATUSES = frozenset({'candidate', 'conditional', 'watch', 'reserve', 'pass', 'selected'})
METRICS = frozenset({'brier', 'log-loss'})
IDENTIFIER = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _identifier(value, name):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(f'{name} must be a safe identifier')
    return value


def _scope_values(values, field, allowed=None):
    if not isinstance(values, list) or not values:
        raise ValueError(f'protocol scope.{field} must be a nonempty array')
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f'invalid protocol scope.{field}')
    if len(set(values)) != len(values) or (allowed and not set(values) <= allowed):
        raise ValueError(f'invalid protocol scope.{field}')


def validate_protocol(protocol):
    if not isinstance(protocol, dict) or type(protocol.get('schemaVersion')) is not int or protocol['schemaVersion'] != 1:
        raise ValueError('protocol requires schemaVersion 1')
    allowed = {'schemaVersion', 'id', 'startsAt', 'endsAt', 'outcomeCutoff', 'registeredAt', 'scope',
               'baselineId', 'primaryMetric', 'minimumPaired', 'minimumFixtureClusters', 'supersedesId'}
    if set(protocol) - allowed:
        raise ValueError('unrecognized protocol fields: ' + ', '.join(sorted(set(protocol) - allowed)))
    _identifier(protocol.get('id'), 'protocol id')
    _identifier(protocol.get('baselineId'), 'baselineId')
    sibling = protocol.get('supersedesId')
    if sibling is not None:
        _identifier(sibling, 'supersedesId')
        if sibling == protocol['id']:
            raise ValueError('a protocol cannot supersede itself')
    window = [timestamp(protocol.get(key)) for key in ('registeredAt', 'startsAt', 'endsAt', 'outcomeCutoff')]
    if not all(window) or not window[0] < window[1] < window[2] <= window[3]:
        raise ValueError('expected registeredAt < startsAt < endsAt <= outcomeCutoff, all with timezones')
    scope = protocol.get('scope')
    if not isinstance(scope, dict) or set(scope) - {'categories', 'statuses', 'competitionIds', 'fixtureIds'}:
        raise ValueError('invalid protocol scope')
    _scope_values(scope.get('categories'), 'categories', CATEGORIES)
    _scope_values(scope.get('statuses'), 'statuses', STATUSES)
    for field in ('competitionIds', 'fixtureIds'):
        if field in scope:
            _scope_values(scope[field], field)
    if protocol.get('primaryMetric') not in METRICS:
        raise ValueError('primaryMetric must be brier or log-loss')
    for field in ('minimumPaired', 'minimumFixtureClusters'):
        if type(protocol.get(field)) is not int or protocol[field] < 1:
            raise ValueError(f'{field} must be a positive integer')
    if protocol['minimumFixtureClusters'] > protocol['minimumPaired']:
        raise ValueError('minimumFixtureClusters cannot exceed minimumPaired')
    return protocol


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _append(directory, artifact, supersedes_id=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (artifact['id'] + '.json')
    if supersedes_id is not None and not (directory / (supersedes_id + '.json')).is_file():
        raise ValueError(f'unknown supersedesId: {supersedes_id}')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(artifact, stream, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    except FileExistsError:
        raise ValueError(f'artifact already exists: {artifact["id"]}') from None
    finally:
        if temporary is not None:
            temporary.unlink()
    return target


def register_protocol(directory, spec):
    """Assign the system time and publish a new protocol. Return its path."""
    if not isinstance(spec, dict) or 'registeredAt' in spec:
        raise ValueError('registeredAt is assigned when a protocol is registered')
    protocol = validate_protocol({**spec, 'registeredAt': _utc_now()})
    return _append(directory, protocol, protocol.get('supersedesId'))


def load_protocol(path):
    path = Path(path)
    with path.open(encoding='utf-8') as stream:
        protocol = validate_protocol(json.load(stream))
    if path.stem != protocol['id']:
        raise ValueError('protocol filename does not match id')
    return protocol


def record_measurement(directory, artifact_id, report, *, supersedes_id=None):
    """Publish an immutable copy of a run, comparison, or evaluation report."""
    _identifier(artifact_id, 'measurement id')
    if not isinstance(report, dict):
        raise ValueError('measurement report must be an object')
    artifact = {'schemaVersion': 1, 'id': artifact_id, 'recordedAt': _utc_now(), 'report': report}
    if supersedes_id is not None:
        _identifier(supersedes_id, 'supersedesId')
        if supersedes_id == artifact_id:
            raise ValueError('a measurement cannot supersede itself')
        artifact['supersedesId'] = supersedes_id
    return _append(directory, artifact, supersedes_id)
