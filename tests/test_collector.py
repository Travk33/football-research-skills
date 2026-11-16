import tempfile
import unittest
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from football_pipeline.collector import Collector, extract_detail

NOW = datetime(2030, 1, 1, 12, tzinfo=timezone.utc)


def match(mid, kickoff, home='1', away='2', **status):
    return {'id': mid, 'home': {'id': home, 'name': 'H'}, 'away': {'id': away, 'name': 'A'},
            'status': {'utcTime': kickoff, 'started': False, 'finished': False, **status}}


def team_fixture(mid, kickoff, finished=True):
    return {'id': mid, 'home': {'id': '1', 'name': 'H'}, 'away': {'id': '3', 'name': 'B'},
            'tournament': {'leagueId': '7', 'name': 'League'},
            'status': {'utcTime': kickoff, 'finished': finished, 'scoreStr': '2 - 1'}}


class CollectorTests(unittest.TestCase):
    def test_timezone_filters_history_and_deduplication(self):
        calls = []
        def transport(url, timeout):
            calls.append(url)
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if parsed.path.endswith('/matches'):
                day = query['date'][0]
                rows = [match('f1', '2030-01-01T23:30:00Z'), match('past', '2030-01-01T11:00:00Z'),
                        match('postponed', '2030-01-01T14:00:00Z', reason={'long': 'Postponed'}),
                        match('other', '2030-01-02T01:00:00Z', home='8')]
                return {'leagues': [{'id': 70, 'primaryId': 7, 'name': 'League', 'matches': rows if day == '20300101' else []}]}
            return {'fixtures': {'allFixtures': {'fixtures': [team_fixture('old', '2029-12-20T12:00:00Z'), team_fixture('same', '2030-01-01T11:30:00Z'), team_fixture('future', '2030-01-02T10:00:00Z')]}}}
        with tempfile.TemporaryDirectory() as directory:
            spec = {'includeTargetDetails': False, 'dates': ['2030-01-02'], 'timezone': 'Asia/Tokyo', 'scope': {'competitionIds': ['7'], 'teamIds': ['1']}, 'historyMatches': 3}
            bundle = Collector(directory, transport=transport).collect(spec, NOW)
            self.assertEqual([f['id'] for f in bundle['fixtures']], ['f1'])
            f = bundle['fixtures'][0]
            self.assertEqual([m['id'] for m in f['history']['home']['matches']], ['old'])
            self.assertEqual(f['history']['away']['matches'], [])
            self.assertTrue(f['history']['away']['gaps'])
            self.assertEqual(len(calls), 5) # two UTC days, two teams and one unique history detail
            self.assertEqual(len({c for c in calls}), len(calls))
            again = Collector(directory, transport=lambda *a: self.fail('should use cache')).collect(spec, NOW)
            self.assertEqual(again['telemetry']['requests'], 0)
            self.assertEqual(again['telemetry']['cacheHits'], 5)

    def test_exclusions_and_failure_visible(self):
        def transport(url, timeout):
            if '/matches?' in url:
                return {'leagues': [{'id': 7, 'name': 'L', 'matches': [match('past', '2030-01-01T11:00:00Z'), match('post', '2030-01-01T14:00:00Z', reason={'long': 'Postponed'}), match('good', '2030-01-01T15:00:00Z')]}]}
            raise OSError('feed unavailable')
        with tempfile.TemporaryDirectory() as directory:
            spec = {'includeTargetDetails': False, 'dates': ['2030-01-01'], 'timezone': 'UTC', 'scope': {'allCompetitions': True}}
            b = Collector(directory, transport=transport).collect(spec, NOW)
            self.assertEqual({e['id'] for e in b['excluded']}, {'past', 'post'})
            self.assertEqual([f['id'] for f in b['fixtures']], ['good'])
            self.assertEqual(len(b['errors']), 2)
            self.assertIn('failed', b['fixtures'][0]['history']['home']['gaps'][0])

    def test_request_limit_and_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = {'includeTargetDetails': False, 'dates': ['2030-01-01'], 'timezone': 'UTC', 'scope': {'fixtureIds': ['missing']}, 'limits': {'maxRequests': 0}}
            b = Collector(directory, transport=lambda *args: self.fail('request limit')).collect(spec, NOW)
            self.assertEqual(b['telemetry']['requests'], 0)
            self.assertEqual(len(b['errors']), 2)
            with self.assertRaises(ValueError):
                Collector(directory).collect({**spec, 'scope': {}}, NOW)


class DetailTests(unittest.TestCase):
    def setUp(self):
        self.row = {'id': '1', 'kickoffUtc': '2026-01-01T12:00:00Z', 'home': {'id': '10'}, 'away': {'id': '20'}}
        self.data = {'general': {'matchId': '1', 'matchTimeUTCDate': '2026-01-01T12:00:00Z', 'homeTeam': {'id': 10}, 'awayTeam': {'id': 20}}, 'header': {'status': {'finished': True, 'reason': {'short': 'FT'}}}, 'content': {'stats': {'Periods': {'All': {'stats': [{'stats': [{'key': 'expected_goals', 'rawStats': [{'value': 1.2}, {'value': 0.8}]}, {'key': 'corners', 'rawStats': [{'value': 0}, None]}]}]}}}, 'matchFacts': {'events': {'events': [{'type': 'Card', 'card': 'Red', 'time': 50, 'isHome': True}]}}}}

    def test_stats_unknowns_and_events(self):
        result = extract_detail(self.data, {'url': 'source'}, self.row)
        self.assertEqual(result['stats']['xG'], {'home': 1.2, 'away': 0.8})
        self.assertEqual(result['stats']['corners'], {'home': 0, 'away': None})
        self.assertIsNone(result['stats']['nonPenaltyXG']['home'])
        self.assertEqual(result['events'][0]['card'], 'Red')
        self.assertIn('nonPenaltyXG unavailable', result['gaps'])

    def test_identity_and_extra_time(self):
        self.data['general']['matchId'] = 'other'
        self.assertEqual(extract_detail(self.data, None, self.row)['stats'], {})
        self.data['general']['matchId'] = '1'
        self.data['header']['status']['reason'] = {'long': 'After penalties'}
        result = extract_detail(self.data, None, self.row)
        self.assertIn('extra time', result['period'])
        self.assertTrue(any('regulation' in gap for gap in result['gaps']))

    def test_retrospective_asof_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = {'includeTargetDetails': False, 'dates': ['2020-01-01'], 'timezone': 'UTC', 'scope': {'allCompetitions': True}}
            b = Collector(directory, transport=lambda *args: {'leagues': []}).collect(spec, datetime(2020, 1, 1, tzinfo=timezone.utc))
            self.assertTrue(any('retrospective' in e['reason'] for e in b['errors']))
            self.assertEqual(b['fixtures'], [])

class TargetDetailTests(unittest.TestCase):
    def transport(self, gender='female', started=False):
        def get(url, timeout):
            if '/matches?' in url:
                return {'leagues': [{'id': 7, 'name': 'L', 'matches': [match('f', '2030-01-01T15:00:00Z')]}]}
            if '/matchDetails?' in url:
                return {'general': {'matchId': 'f', 'matchTimeUTCDate': '2030-01-01T15:00:00Z', 'homeTeam': {'id': 1}, 'awayTeam': {'id': 2}, 'gender': gender}, 'header': {'status': {'started': started}}, 'content': {'lineup': {'lineupType': 'predicted', 'homeTeam': {'starters': [{'id': 9, 'name': 'Player'}]}}}}
            return {'fixtures': {'allFixtures': {'fixtures': []}}}
        return get

    def test_gender_verified_and_missing_venue_projected_lineup(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = {'dates': ['2030-01-01'], 'timezone': 'UTC', 'scope': {'gender': 'female', 'allCompetitions': True}, 'historyMatches': 0}
            result = Collector(directory, transport=self.transport()).collect(spec, NOW)
            fixture = result['fixtures'][0]
            self.assertEqual(fixture['snapshot']['gender'], 'female')
            self.assertIsNone(fixture['snapshot']['venue'])
            self.assertTrue(any('venue unavailable' in gap for gap in fixture['gaps']))
            self.assertEqual(fixture['snapshot']['lineup']['state'], 'projected')
            self.assertEqual(fixture['coverage']['historyDetailsSucceeded']['home'], 0)

    def test_gender_mismatch_and_unknown_due_to_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = {'dates': ['2030-01-01'], 'timezone': 'UTC', 'scope': {'gender': 'male', 'allCompetitions': True}}
            result = Collector(directory, transport=self.transport()).collect(spec, NOW)
            self.assertEqual(result['excluded'][0]['reason'], 'verified gender outside scope')
        with tempfile.TemporaryDirectory() as directory:
            spec['limits'] = {'maxRequests': 1}
            result = Collector(directory, transport=self.transport()).collect(spec, NOW)
            self.assertEqual(result['excluded'][0]['reason'], 'gender unresolved')
            self.assertTrue(any('Gender requested' in error['reason'] for error in result['errors']))

    def test_started_in_target_detail_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = {'dates': ['2030-01-01'], 'timezone': 'UTC', 'scope': {'allCompetitions': True}}
            result = Collector(directory, transport=self.transport(started=True)).collect(spec, NOW)
            self.assertEqual(result['fixtures'], [])
            self.assertIn('started', result['excluded'][0]['reason'])


class DiscoveryTests(unittest.TestCase):
    def test_day_feed_only_without_target_details_or_history(self):
        calls = []
        def transport(url, timeout):
            calls.append(url)
            return {'leagues': [{'id': 7, 'name': 'League', 'matches': [match('f', '2030-01-01T15:00:00Z')]}]}
        with tempfile.TemporaryDirectory() as directory:
            spec = {'dates': ['2030-01-01'], 'timezone': 'UTC', 'scope': {'allCompetitions': True}, 'historyMatches': 0, 'historyDetails': 0, 'includeTargetDetails': False}
            result = Collector(directory, transport=transport).collect(spec, NOW)
            self.assertEqual(len(result['fixtures']), 1)
            self.assertEqual(len(calls), 1)
            self.assertIn('/matches?', calls[0])
            self.assertEqual(result['fixtures'][0]['history']['home']['matches'], [])
