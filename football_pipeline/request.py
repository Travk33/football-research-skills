"""Explicit, variable research scopes and bounded runtime configuration."""
import copy
import hashlib
import json
import re
from datetime import date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CATEGORIES = {'wins-btts', 'other-markets', 'bet-builders'}
DEFAULT_ROUTING = {
    'retrieval': {'model': 'gpt-6-luna', 'effort': 'medium'},
    'review': {'model': 'gpt-6.2-sol', 'effort': 'high'},
    'lead': {'model': 'gpt-6.2-astra', 'effort': 'high'},
}
DEFAULT_LIMITS = {
    'maxRequests': 300, 'batchSize': 6, 'leadBatchSize': 12,
    'deepBatchSize': 3, 'reviewBatchSize': 3, 'maxModelCalls': 40,
    'maxParallel': 2, 'timeoutSeconds': 180,
    'maxBuilderFixtures': 5, 'quoteMaxAgeSeconds': 900,
    'lineupMaxAgeSeconds': 7200,
}
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _ids(value, label):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.isdigit() for v in value):
        raise ValueError(label + ' must be an array of provider ID strings (digits only)')
    return sorted(set(value))


def validate_request(value):
    if not isinstance(value, dict):
        raise ValueError('request must be an object')
    permitted = {'schemaVersion', 'id', 'dates', 'timezone', 'scope', 'categories', 'historyMatches',
                 'historyDetails', 'includeTargetDetails', 'limits', 'routing', 'builderFixtureIds', 'description', 'comparison'}
    unknown = set(value) - permitted
    if unknown:
        raise ValueError('unknown request fields: ' + ', '.join(sorted(unknown)))
    spec = copy.deepcopy(value)
    if type(spec.get('schemaVersion')) is not int or spec['schemaVersion'] != 1:
        raise ValueError('schemaVersion must be 1')
    if not isinstance(spec.get('id'), str) or not ID.fullmatch(spec['id']):
        raise ValueError('id must be a short safe artifact identifier')
    dates = spec.get('dates')
    if not isinstance(dates, list) or not dates:
        raise ValueError('dates must contain requested local calendar dates')
    try:
        if any(not isinstance(d, str) or date.fromisoformat(d).isoformat() != d for d in dates):
            raise ValueError()
    except ValueError:
        raise ValueError('dates must use YYYY-MM-DD') from None
    spec['dates'] = sorted(set(dates))
    zone = spec.setdefault('timezone', 'Europe/London')
    try:
        ZoneInfo(zone)
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        raise ValueError('timezone must be a valid IANA timezone') from None
    scope = spec.get('scope')
    if not isinstance(scope, dict) or set(scope) - {'competitionIds', 'fixtureIds', 'teamIds', 'allCompetitions', 'gender'}:
        raise ValueError('scope requires only explicit competitionIds, fixtureIds, teamIds or allCompetitions')
    for field in ('competitionIds', 'fixtureIds', 'teamIds'):
        scope[field] = _ids(scope.get(field, []), 'scope.' + field)
    if type(scope.get('allCompetitions', False)) is not bool:
        raise ValueError('allCompetitions must be boolean')
    if 'gender' in scope and scope['gender'] not in {'male', 'female'}:
        raise ValueError('scope.gender must be male or female; omit for unrestricted gender')
    if not any(scope[k] for k in ('competitionIds', 'fixtureIds', 'teamIds')) and not scope.get('allCompetitions'):
        raise ValueError('empty filters require allCompetitions: true; no implicit worldwide scope')
    categories = spec.get('categories')
    if not isinstance(categories, list) or not categories or any(not isinstance(c, str) or c not in CATEGORIES for c in categories):
        raise ValueError('categories must name wins-btts, other-markets and/or bet-builders')
    spec['categories'] = sorted(set(categories))
    if type(spec.setdefault('includeTargetDetails', True)) is not bool:
        raise ValueError('includeTargetDetails must be boolean')
    history = spec.setdefault('historyMatches', 8)
    detail = spec.setdefault('historyDetails', min(3, history) if type(history) is int else 3)
    if type(history) is not int or not 0 <= history <= 100:
        raise ValueError('historyMatches must be an integer from 0 to 100')
    if type(detail) is not int or not 0 <= detail <= history:
        raise ValueError('historyDetails must be from 0 to historyMatches')
    given_limits = spec.get('limits', {})
    if not isinstance(given_limits, dict) or set(given_limits) - set(DEFAULT_LIMITS):
        raise ValueError('unknown limits field')
    spec['limits'] = {**DEFAULT_LIMITS, **given_limits}
    for field, number in spec['limits'].items():
        if type(number) is not int or number < 1:
            raise ValueError(field + ' must be a positive integer')
    if spec['limits']['maxParallel'] > 8:
        raise ValueError('maxParallel is bounded to 8; batch more work sequentially')
    routes = spec.get('routing', {})
    if not isinstance(routes, dict) or set(routes) - set(DEFAULT_ROUTING):
        raise ValueError('routing roles must be retrieval, review or lead')
    spec['routing'] = {}
    for role, default in DEFAULT_ROUTING.items():
        route = {**default, **routes.get(role, {})} if isinstance(routes.get(role, {}), dict) else None
        if not route or set(route) != {'model', 'effort'} or not isinstance(route['model'], str) or not re.fullmatch(r'[A-Za-z0-9._-]+', route['model']):
            raise ValueError('invalid model route for ' + role)
        if route['effort'] not in {'low', 'medium', 'high', 'xhigh', 'max', 'ultra'}:
            raise ValueError('invalid effort for ' + role)
        spec['routing'][role] = route
    builders = _ids(spec.get('builderFixtureIds', []), 'builderFixtureIds')
    if 'bet-builders' in spec['categories']:
        builders = builders or scope['fixtureIds']
        if not builders:
            raise ValueError('builder research requires an explicit fixture subset')
        if len(builders) > spec['limits']['maxBuilderFixtures']:
            raise ValueError('builder fixture subset exceeds the requested limit')
        if scope['fixtureIds'] and not set(builders).issubset(scope['fixtureIds']):
            raise ValueError('builder fixtures must lie within scope.fixtureIds')
    elif builders:
        raise ValueError('builderFixtureIds provided without bet-builders category')
    spec['builderFixtureIds'] = builders
    return spec
