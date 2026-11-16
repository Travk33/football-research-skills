"""Bounded, provenance-preserving FotMob fixture and team-history collector."""
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .cache import Cache

BASE = 'https://www.fotmob.com/api/data/'
UTC = timezone.utc


def _dt(value):
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return d.astimezone(UTC) if d.tzinfo else None
    except (AttributeError, TypeError, ValueError):
        return None


def _iso(value):
    return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')


def _identity(value):
    return {'id': str(value['id']) if value.get('id') is not None else None, 'name': value.get('name')}


def _transport(url, timeout):
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}), timeout=timeout) as response:
        return json.load(response)


def league_ids_for_fixture(fixture):
    return {v for v in (fixture['competition'].get('id'), fixture['competition'].get('primaryId')) if v is not None}


def extract_detail(data, source, match):
    """Read provider match stats without assuming absent observations equal zero."""
    detail = {'provider': 'FotMob', 'source': source, 'period': None, 'stats': {}, 'events': None, 'gaps': []}
    names = {'expected_goals': 'xG', 'expected_goals_non_penalty': 'nonPenaltyXG',
             'total_shots': 'shots', 'ShotsOnTarget': 'shotsOnTarget',
             'corners': 'corners', 'yellow_cards': 'yellowCards', 'red_cards': 'redCards',
             'BallPossesion': 'possession'}
    if not isinstance(data, dict):
        detail['gaps'].append('Match detail unavailable or request limit reached')
        return detail
    general = data.get('general') or {}
    header = data.get('header') or {}
    status = header.get('status') or {}
    home = general.get('homeTeam') or {}
    away = general.get('awayTeam') or {}
    if (str(general.get('matchId')) != match['id'] or
        _dt(general.get('matchTimeUTCDate')) != _dt(match['kickoffUtc']) or
        str(home.get('id')) != match['home']['id'] or str(away.get('id')) != match['away']['id'] or
        not status.get('finished') or status.get('cancelled') or status.get('awarded')):
        detail['gaps'].append('Match detail identity, date, teams or completed status did not match history')
        return detail
    reason = status.get('reason') or {}
    reason_text = ' '.join(str(reason.get(k, '')) for k in ('short', 'long', 'shortKey', 'longKey')).lower()
    halfs = status.get('halfs') or {}
    extra = bool(halfs.get('firstExtraHalfStarted') or halfs.get('secondExtraHalfStarted') or
                 'penalt' in reason_text or 'extra' in reason_text)
    detail['period'] = 'provider All; includes or may include extra time' if extra else 'provider All; regulation-time scope not independently verified'
    if extra:
        detail['gaps'].append('All-period statistics may include extra time; do not treat as regulation-time totals')
    groups = (((data.get('content') or {}).get('stats') or {}).get('Periods') or {}).get('All') or {}
    for group in groups.get('stats', []):
        for stat in group.get('stats', []):
            key = names.get(stat.get('key'))
            raw = stat.get('rawStats')
            if key and isinstance(raw, list) and len(raw) == 2:
                values = [x.get('value') if isinstance(x, dict) else None for x in raw]
                if any(v is not None for v in values):
                    detail['stats'][key] = {'home': values[0], 'away': values[1]}
    for name in names.values():
        if name not in detail['stats']:
            detail['stats'][name] = {'home': None, 'away': None}
            detail['gaps'].append(name + ' unavailable')
    event_container = ((data.get('content') or {}).get('matchFacts') or {}).get('events') or {}
    raw_events = event_container.get('events')
    if isinstance(raw_events, list):
        events = []
        for event in raw_events:
            event_type = str(event.get('type', '')).lower()
            card = str(event.get('card', '')).lower()
            penalty = 'penalt' in ' '.join(str(event.get(k, '')) for k in ('type', 'goalDescription', 'goalDescriptionKey', 'shotType')).lower()
            shot = event.get('shotmapEvent') or {}
            penalty = penalty or 'penalt' in str(shot.get('situation', '')).lower()
            if penalty or (event_type == 'card' and 'red' in card):
                events.append({k: event.get(k) for k in ('type', 'time', 'overloadTime', 'isHome', 'card', 'goalDescription', 'isPenaltyShootoutEvent')})
        detail['events'] = events
        detail['eventNote'] = 'Reported penalty and red-card events only; an empty list does not establish complete coverage.'
    else:
        detail['gaps'].append('Penalty/red-card event feed unavailable')
    return detail


class Collector:
    def __init__(self, cache_dir, max_requests=200, timeout=20, transport=None):
        self.cache = Cache(cache_dir)
        self.max_requests = max_requests
        self.timeout = timeout
        self.transport = transport or _transport

    def collect(self, spec, now=None):
        requested_as_of = now
        now = now or datetime.now(UTC)
        if now.tzinfo is None:
            raise ValueError('now must be timezone-aware')
        now = now.astimezone(UTC)
        zone = ZoneInfo(spec['timezone'])
        dates = {date.fromisoformat(d) for d in spec['dates']}
        scope = spec.get('scope', {})
        comp = {str(x) for x in scope.get('competitionIds', [])}
        ids = {str(x) for x in scope.get('fixtureIds', [])}
        teams = {str(x) for x in scope.get('teamIds', [])}
        if not (comp or ids or teams or scope.get('allCompetitions')):
            raise ValueError('empty scope requires allCompetitions: true')
        limits = spec.get('limits', {})
        max_requests = min(self.max_requests, limits.get('maxRequests', self.max_requests))
        timeout = min(self.timeout, limits.get('timeoutSeconds', self.timeout))
        bundle = {'schemaVersion': 1, 'scope': {**scope, 'dates': sorted(d.isoformat() for d in dates), 'timezone': spec['timezone']}, 'collectedAt': None, 'requestedAsOf': _iso(now) if requested_as_of else None, 'fixtures': [], 'excluded': [], 'errors': [], 'telemetry': {'requests': 0, 'cacheHits': 0, 'maxRequests': max_requests}}
        memory = {}

        def fetch(resource, params, cache_resource=None):
            url = BASE + resource + '?' + urlencode(params)
            if url in memory:
                return memory[url]
            cache_resource = cache_resource or resource
            # Cache age is measured against real wall clock, not an injected decision time.
            hit, data, stamp = self.cache.get(url, cache_resource)
            if hit:
                bundle['telemetry']['cacheHits'] += 1
                result = (data, {'url': url, 'retrievedAt': stamp, 'cached': True})
            elif bundle['telemetry']['requests'] >= max_requests:
                bundle['errors'].append({'url': url, 'reason': 'maxRequests exhausted'})
                result = (None, None)
            else:
                bundle['telemetry']['requests'] += 1
                try:
                    data = self.transport(url, timeout)
                    stamp = self.cache.put(url, cache_resource, data)
                    result = (data, {'url': url, 'retrievedAt': stamp, 'cached': False})
                except Exception as exc:
                    bundle['errors'].append({'url': url, 'reason': str(exc), 'type': type(exc).__name__})
                    result = (None, None)
            if requested_as_of is not None and result[1] and _dt(result[1]['retrievedAt']) > now:
                bundle['errors'].append({'url': url, 'reason': 'source was retrieved after the requested as-of time; retrospective reconstruction is unavailable'})
                result = (None, None)
            memory[url] = result
            return result

        # Map each local day to every UTC calendar day it overlaps (DST included).
        utc_days = set()
        for day in dates:
            start = datetime.combine(day, time.min, zone).astimezone(UTC)
            end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC) - timedelta(microseconds=1)
            current = start.date()
            while current <= end.date():
                utc_days.add(current)
                current += timedelta(days=1)
        found = {}
        for day in sorted(utc_days):
            data, ref = fetch('matches', {'date': day.strftime('%Y%m%d')})
            if not isinstance(data, dict) or not isinstance(data.get('leagues'), list):
                if data is not None:
                    bundle['errors'].append({'source': ref, 'reason': 'invalid matches response'})
                continue
            for league in data['leagues']:
                for match in league.get('matches', []):
                    mid = str(match.get('id', ''))
                    status = match.get('status') or {}
                    kickoff = _dt(status.get('utcTime'))
                    if not mid or not kickoff or kickoff.astimezone(zone).date() not in dates:
                        continue
                    league_ids = {str(league.get(k)) for k in ('id', 'primaryId', 'parentLeagueId') if league.get(k) is not None}
                    home, away = match.get('home') or {}, match.get('away') or {}
                    if (comp and not comp.intersection(league_ids)) or (ids and mid not in ids) or (teams and not teams.intersection({str(home.get('id')), str(away.get('id'))})):
                        continue
                    found.setdefault(mid, (match, league, ref, kickoff))
        for mid, (match, league, ref, kickoff) in sorted(found.items(), key=lambda item: (item[1][3], item[0])):
            status = match.get('status') or {}
            reason = status.get('reason') or {}
            label = ' '.join(str(reason.get(k, '')) for k in ('short', 'shortKey', 'long', 'longKey')).lower()
            excluded = None
            if status.get('cancelled') or 'cancel' in label:
                excluded = 'cancelled'
            elif 'postpon' in label or 'suspend' in label or 'abandon' in label:
                excluded = 'postponed or suspended'
            elif status.get('started') or status.get('finished') or kickoff <= now:
                excluded = 'started or past kickoff'
            elif not match.get('home', {}).get('id') or not match.get('away', {}).get('id'):
                excluded = 'missing team identity'
            if excluded:
                bundle['excluded'].append({'id': mid, 'kickoffUtc': _iso(kickoff), 'reason': excluded, 'source': ref})
                continue
            fixture = {'id': mid, 'home': _identity(match['home']), 'away': _identity(match['away']), 'kickoffUtc': _iso(kickoff), 'competition': {'id': str(league.get('id')), 'name': league.get('name'), 'primaryId': str(league.get('primaryId')) if league.get('primaryId') is not None else None}, 'status': 'scheduled', 'snapshot': {'status': {k: status[k] for k in ('utcTime', 'started', 'finished', 'cancelled', 'reason') if k in status}, 'capturedAt': ref['retrievedAt']}, 'sources': [ref], 'history': {}, 'gaps': ['No verified prices or bookmaker market terms collected', 'Provider lineup and availability require independent freshness and confirmation checks', 'Match-level statistics may be missing; see each history detail and gaps']}
            if spec.get('includeTargetDetails', True) or scope.get('gender'):
                target, target_ref = fetch('matchDetails', {'matchId': mid}, 'targetDetails')
                general = target.get('general') or {} if isinstance(target, dict) else {}
                header = target.get('header') or {} if isinstance(target, dict) else {}
                target_status = header.get('status') or {}
                valid = (str(general.get('matchId')) == mid and _dt(general.get('matchTimeUTCDate')) == kickoff
                         and str((general.get('homeTeam') or {}).get('id')) == fixture['home']['id']
                         and str((general.get('awayTeam') or {}).get('id')) == fixture['away']['id'])
                if valid:
                    fixture['sources'].append(target_ref)
                    fixture['snapshot']['targetStatus'] = {k: target_status[k] for k in ('utcTime', 'started', 'finished', 'cancelled', 'reason') if k in target_status}
                    content = target.get('content') or {}
                    facts = content.get('matchFacts') or {}
                    venue = (facts.get('infoBox') or {}).get('Stadium') or {}
                    fixture['snapshot']['venue'] = {k: venue.get(k) for k in ('name', 'city', 'country')} if venue.get('name') else None
                    if not fixture['snapshot']['venue']:
                        fixture['gaps'].append('Target venue unavailable from provider')
                    fixture['snapshot']['gender'] = general.get('gender') if general.get('gender') in ('male', 'female') else None
                    lineup = content.get('lineup') or {}
                    lineup_type = str(lineup.get('lineupType') or 'unavailable').lower()
                    lineup_state = 'confirmed' if lineup_type == 'confirmed' else 'projected' if lineup_type in ('predicted', 'projected', 'expected') else 'unavailable'
                    fixture['snapshot']['lineup'] = {'state': lineup_state, 'providerType': lineup_type, 'source': target_ref}
                    if lineup_state != 'unavailable':
                        for side in ('home', 'away'):
                            side_lineup = lineup.get(side + 'Team') or {}
                            fixture['snapshot']['lineup'][side] = [{'id': str(p.get('id')) if p.get('id') is not None else None, 'name': p.get('name')} for p in side_lineup.get('starters', [])]
                    if target_status.get('started') or target_status.get('finished') or target_status.get('cancelled'):
                        bundle['excluded'].append({'id': mid, 'kickoffUtc': _iso(kickoff), 'reason': 'target details report started, finished or cancelled', 'source': target_ref})
                        continue
                    reason_text = str(target_status.get('reason') or {}).lower()
                    if any(word in reason_text for word in ('postpon', 'suspend', 'abandon')):
                        bundle['excluded'].append({'id': mid, 'kickoffUtc': _iso(kickoff), 'reason': 'target details report postponed or suspended', 'source': target_ref})
                        continue
                else:
                    fixture['gaps'].append('Target detail unavailable or identity/date/teams did not match')
                    fixture['snapshot']['venue'] = None
                    fixture['snapshot']['gender'] = None
                if scope.get('gender') and fixture['snapshot']['gender'] != scope['gender']:
                    if fixture['snapshot']['gender'] is None:
                        bundle['errors'].append({'fixtureId': mid, 'reason': 'Gender requested but target detail is unavailable or unverified'})
                        reason = 'gender unresolved'
                    else:
                        reason = 'verified gender outside scope'
                    bundle['excluded'].append({'id': mid, 'kickoffUtc': _iso(kickoff), 'reason': reason, 'source': target_ref})
                    continue
            else:
                fixture['gaps'].append('Target details not requested; gender, venue and lineup unverified')
            detail_requested = min(spec.get('historyDetails', 3), spec.get('historyMatches', 8))
            fixture['coverage'] = {'historyDetailsRequestedPerTeam': detail_requested, 'historyDetailsSucceeded': {}}
            for side in ('home', 'away'):
                if spec.get('historyMatches', 8) == 0:
                    fixture['history'][side] = {'matches': [], 'gaps': ['Team history not requested'], 'source': None}
                    fixture['coverage']['historyDetailsSucceeded'][side] = 0
                    continue
                team = fixture[side]
                data, team_ref = fetch('teams', {'id': team['id']})
                ledger = {'matches': [], 'gaps': [], 'source': team_ref}
                if isinstance(data, dict):
                    raw = (data.get('fixtures') or {}).get('allFixtures') or {}
                    rows = raw.get('fixtures') if isinstance(raw, dict) else None
                    if not isinstance(rows, list):
                        ledger['gaps'].append('Team fixture history unavailable')
                    else:
                        for row in rows:
                            rs = row.get('status') or {}
                            when = _dt(rs.get('utcTime'))
                            # Finished at source and safely before the decision capture; scores for recent ongoing matches cannot leak.
                            if str(row.get('id')) == mid or not when or when >= kickoff or when + timedelta(hours=3) > now or not rs.get('finished') or rs.get('cancelled') or rs.get('awarded'):
                                continue
                            h, a = row.get('home') or {}, row.get('away') or {}
                            if team['id'] not in {str(h.get('id')), str(a.get('id'))}:
                                continue
                            ledger['matches'].append({'id': str(row.get('id')), 'kickoffUtc': _iso(when), 'home': _identity(h), 'away': _identity(a), 'competition': {'id': str((row.get('tournament') or {}).get('leagueId')) if (row.get('tournament') or {}).get('leagueId') is not None else None, 'name': (row.get('tournament') or {}).get('name')}, 'score': rs.get('scoreStr'), 'scoreNote': (rs.get('reason') or {}).get('long'), 'source': team_ref})
                        ledger['matches'].sort(key=lambda m: (m['kickoffUtc'], m['id']), reverse=True)
                        comparable = [m for m in ledger['matches'] if m['competition']['id'] in league_ids_for_fixture(fixture)]
                        summary = {'basis': 'provider available fixture feed matching target competition ID; season coverage not independently verified', 'sampleSize': len(comparable), 'firstKickoffUtc': comparable[-1]['kickoffUtc'] if comparable else None, 'lastKickoffUtc': comparable[0]['kickoffUtc'] if comparable else None, 'scoreSampleSize': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'source': team_ref}
                        for item in comparable:
                            score = re.fullmatch(r'\s*(\d+)\s*-\s*(\d+)\s*', str(item.get('score') or ''))
                            if not score or str(item.get('scoreNote') or '').lower() not in ('full-time', 'full time'):
                                continue
                            home_goals, away_goals = (int(n) for n in score.groups())
                            gf, ga = (home_goals, away_goals) if item['home']['id'] == team['id'] else (away_goals, home_goals)
                            summary['scoreSampleSize'] += 1
                            summary['goalsFor'] += gf
                            summary['goalsAgainst'] += ga
                            summary['wins' if gf > ga else 'draws' if gf == ga else 'losses'] += 1
                        summary['scoreNote'] = 'Only provider Full-Time scores counted; extra-time, penalties and unlabelled scores excluded.'
                        ledger['comparableSummary'] = summary
                        ledger['matches'] = ledger['matches'][:spec.get('historyMatches', 8)]
                        detail_count = min(spec.get('historyDetails', 3), spec.get('historyMatches', 8))
                        for historical in ledger['matches'][:detail_count]:
                            detail, detail_ref = fetch('matchDetails', {'matchId': historical['id']})
                            historical['detail'] = extract_detail(detail, detail_ref, historical)
                        if len(ledger['matches']) > detail_count:
                            ledger['gaps'].append('Match-level details not requested for all history rows')
                        if len(ledger['matches']) < spec.get('historyMatches', 8):
                            ledger['gaps'].append('Fewer completed eligible matches available than requested')
                        ledger['gaps'].append('Scores are provider-reported final scores; competition comparability and regulation-time settlement require review')
                else:
                    ledger['gaps'].append('Team history fetch failed or request limit reached')
                fixture['history'][side] = ledger
                fixture['coverage']['historyDetailsSucceeded'][side] = sum(1 for m in ledger['matches'] if m.get('detail') and any(v.get('home') is not None or v.get('away') is not None for v in m['detail']['stats'].values()))
                if team_ref:
                    fixture['sources'].append(team_ref)
            bundle['fixtures'].append(fixture)
        if ids:
            missing = sorted(ids - set(found))
            if missing:
                bundle['errors'].append({'fixtureIds': missing, 'reason': 'Requested fixtures not found in retrieved dates/scope; check failed date feeds and filters'})
        finished_at = datetime.now(UTC)
        bundle['collectedAt'] = _iso(finished_at)
        # A fixture can start while the collector is fetching histories.
        decision_time = max(now, finished_at)
        retained = []
        for fixture in bundle['fixtures']:
            if _dt(fixture['kickoffUtc']) <= decision_time:
                bundle['excluded'].append({'id': fixture['id'], 'kickoffUtc': fixture['kickoffUtc'], 'reason': 'started or passed kickoff during collection', 'source': fixture['sources'][0]})
            else:
                retained.append(fixture)
        bundle['fixtures'] = retained
        return bundle
