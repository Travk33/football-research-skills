import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from football_pipeline.evaluation import compare_costs, evaluate_journal, usage_report
from football_pipeline.protocol import load_protocol, record_measurement, register_protocol
from scripts import journal


ROOT = Path(__file__).resolve().parents[1]
TIMES = {
    'registered': '2020-01-01T00:00:00Z',
    'start': '2020-01-02T00:00:00Z',
    'forecast': '2020-01-03T12:00:00Z',
    'kickoff': '2020-01-03T20:00:00Z',
    'outcome': '2020-01-03T22:00:00Z',
    'end': '2020-01-04T00:00:00Z',
    'cutoff': '2020-01-05T00:00:00Z',
}
RATES = {
    'currency': 'USD',
    'rates': [
        {'model': 'reported-a', 'effectiveFrom': '2020-01-01', 'effectiveTo': '2020-01-03',
         'inputPerMillion': 2, 'cachedInputPerMillion': 1, 'outputPerMillion': 4},
        {'model': 'reported-a', 'effectiveFrom': '2020-01-03',
         'inputPerMillion': 4, 'cachedInputPerMillion': 1, 'outputPerMillion': 9},
    ],
}


def _call(started_at, usage=None):
    if usage is None:
        usage = {'input_tokens': 1_000_000, 'cached_input_tokens': 200_000, 'output_tokens': 100_000}
    return {'requestedModel': 'requested-a', 'reportedModel': 'reported-a', 'usage': usage,
            'startedAt': started_at, 'status': 'completed'}


def _manifest(*calls):
    return {'mode': 'execute', 'status': 'completed', 'scope': {'fixtureIds': ['1', '2']},
            'categories': ['wins-btts'], 'evidenceHash': 'same-evidence', 'specHash': 'one',
            'sourceTelemetry': {'requests': 12, 'cacheHits': 5}, 'calls': list(calls),
            'tasks': [{'stage': 'lead', 'fixtureIds': ['1', '2'],
                       'directions': ['1/wins-btts/btts-yes', '2/wins-btts/btts-yes']}]}


def _decision(id, status='candidate', fixture_id=None):
    return {'id': id, 'type': 'decision', 'cohort': 'prospective', 'status': status,
            'category': 'wins-btts', 'fixture': {'id': fixture_id or id, 'home': 'Home', 'away': 'Away'},
            'market': {'resolved': True}, 'originalTime': {'value': TIMES['forecast'], 'precision': 'exact',
                                                          'preKickoffEvidence': 'verified'},
            'kickoff': TIMES['kickoff'], 'recordedAt': TIMES['forecast'], 'appendedAt': TIMES['forecast'],
            'probability': 0.8, 'probabilitySource': 'model-forecast', 'odds': 2.0, 'conditions': 'met',
            'baselineForecast': {'id': 'reference', 'probability': 0.4, 'recordedAt': TIMES['forecast'],
                                 'settlement': 'onPitchOutcome'}}


def _outcome(id, value='won', **overrides):
    return {'id': 'outcome-' + id, 'type': 'outcome', 'decisionId': id, 'evidenceLevel': 'verified',
            'recordedAt': TIMES['outcome'], 'appendedAt': TIMES['outcome'], 'sources': ['match-result'],
            'onPitchOutcome': value, 'ruleBasedOutcome': 'won', 'bookmakerSettlement': 'won', **overrides}


def _protocol():
    return {'schemaVersion': 1, 'id': 'protocol', 'registeredAt': TIMES['registered'],
            'startsAt': TIMES['start'], 'endsAt': TIMES['end'], 'outcomeCutoff': TIMES['cutoff'],
            'scope': {'categories': ['wins-btts'], 'statuses': ['selected', 'candidate', 'pass']},
            'baselineId': 'reference', 'primaryMetric': 'brier', 'minimumPaired': 20, 'minimumFixtureClusters': 20}


class UsageTests(unittest.TestCase):
    def test_actual_usage_and_dated_cached_api_estimate(self):
        manifest = _manifest(_call('2020-01-02T12:00:00Z'), _call('2020-01-03T12:00:00Z'))
        report = usage_report(manifest, RATES)
        self.assertEqual(report['usage'], {'inputTokens': 2_000_000, 'cachedInputTokens': 400_000,
                                           'outputTokens': 200_000})
        self.assertAlmostEqual(report['estimatedApiCost']['amount'], 6.5)
        self.assertEqual(report['requestedModels'], {'requested-a': 2})
        self.assertEqual(report['reportedModels'], {'reported-a': 2})
        self.assertIsNone(report['subscriptionCost'])
        self.assertEqual(report['sourceCacheHits'], 5)

    def test_missing_usage_identity_and_plan_remain_unavailable(self):
        first = _call('2020-01-02T12:00:00Z', {'input_tokens': 10, 'output_tokens': 4})
        second = _call('2020-01-03T12:00:00Z')
        second['reportedModel'] = None
        report = usage_report(_manifest(first, second), RATES)
        self.assertIsNone(report['usage']['cachedInputTokens'])
        self.assertEqual(report['usage']['outputTokens'], 100_004)
        self.assertIsNone(report['estimatedApiCost'])
        self.assertEqual(report['apiEstimateUnavailableReasons'],
                         ['incomplete-reported-token-usage', 'missing-reported-model-or-call-time'])
        self.assertIsNone(usage_report({'mode': 'plan'})['usage']['inputTokens'])

    def test_compatible_runs_allow_different_batching_and_routing(self):
        baseline = _manifest(_call('2020-01-02T12:00:00Z'), _call('2020-01-02T12:01:00Z'))
        candidate = _manifest(_call('2020-01-02T18:00:00Z'))
        candidate['tasks'] = [{'stage': 'lead', 'fixtureIds': [id], 'directions': [f'{id}/wins-btts/btts-yes']}
                              for id in ('1', '2')]
        candidate['specHash'] = 'changed-routing'
        result = compare_costs(usage_report(baseline, RATES), usage_report(candidate, RATES))
        self.assertTrue(result['workComparable'])
        self.assertEqual(result['estimatedApiCostReduction']['percent'], 50)
        self.assertEqual(result['modelCallReduction']['percent'], 50)
        self.assertIsNone(result['subscriptionCostReduction'])
        self.assertIsNone(compare_costs(baseline, candidate)['estimatedApiCostReduction'])

    def test_comparison_rejects_same_run_incomplete_work_or_changed_evidence(self):
        baseline = _manifest(_call('2020-01-02T12:00:00Z'))
        self.assertIn('same-run-measurement', compare_costs(baseline, copy.deepcopy(baseline))['reasons'])
        candidate = _manifest(_call('2020-01-02T13:00:00Z'))
        candidate['evidenceHash'] = 'new-evidence'
        candidate['status'] = 'partial'
        candidate['tasks'][0]['directions'] = ['1/wins-btts/btts-yes']
        result = compare_costs(baseline, candidate)
        self.assertFalse(result['workComparable'])
        self.assertIsNone(result['modelCallReduction'])
        self.assertEqual(set(result['reasons']), {'both-runs-must-complete-executed-work',
                                                  'missing-or-different-evidenceHash', 'missing-or-different-workloadHash'})


class EvaluationTests(unittest.TestCase):
    def test_current_historical_journal_cannot_establish_predictive_performance(self):
        events = journal.load(ROOT / 'journal' / 'data')
        self.assertGreaterEqual(len(events), 146)
        report = evaluate_journal(events)
        self.assertGreaterEqual(report['coverage']['decisionCohorts']['historical-import'], 69)
        self.assertEqual(report['coverage']['scoredProspectiveForecasts'], 0)
        self.assertEqual(report['predictiveSuperiority'], 'unestablished')
        self.assertEqual(report['observations'], [])

    def test_pass_and_late_revision_preserve_roles_and_ordinary_outcome(self):
        selected = _decision('selected', 'selected')
        passed = _decision('pass', 'pass')
        late = {'id': 'late-select', 'type': 'status_revision', 'decisionId': 'pass',
                'effectiveAt': TIMES['forecast'], 'recordedAt': TIMES['forecast'], 'appendedAt': TIMES['outcome'],
                'status': 'selected', 'preKickoffEvidence': 'verified', 'conditions': 'met', 'odds': 2.0}
        report = evaluate_journal([selected, passed, late, _outcome('selected', 'lost'), _outcome('pass')])
        self.assertEqual(report['selected']['binaryHitRate'], 0)
        self.assertEqual(report['researchDirections']['pass']['binaryHitRate'], 1)
        self.assertEqual(report['selected']['forecastScores']['sampleSize'], 1)
        pair = report['pairedComparisons']['reference']
        self.assertEqual(pair['sampleSize'], 2)
        self.assertIsNone(pair['differences']['brier']['confidenceInterval'])
        self.assertEqual(report['predictiveSuperiority'], 'unestablished')

    def test_unverified_capture_and_odds_derived_probabilities_are_rejected(self):
        backdated = _decision('backdated')
        backdated['appendedAt'] = TIMES['outcome']
        derived = _decision('derived')
        derived.update(probability=0.5, probabilitySource='odds-reciprocal')
        undocumented = _decision('undocumented')
        undocumented['probability'] = 0.5
        del undocumented['probabilitySource']
        demo = _decision('demo')
        demo['cohort'] = 'demo'
        report = evaluate_journal([backdated, derived, undocumented, demo, _outcome('backdated'),
                                   _outcome('derived'), _outcome('undocumented'), _outcome('demo')])
        self.assertEqual(report['coverage']['scoredProspectiveForecasts'], 0)
        self.assertEqual(report['coverage']['forecastGateReasons'], {'capture-before-kickoff-unverified': 1,
                         'odds-derived-probability': 1, 'undocumented-probability-equals-reciprocal-odds': 1})

    def test_outcome_corrections_respect_cutoff_and_protocol_pairing(self):
        first = _outcome('first', 'lost')
        correction = _outcome('first', 'won', supersedesId=first['id'])
        correction.update(id='corrected', recordedAt='2020-01-06T00:00:00Z', appendedAt='2020-01-06T00:00:00Z')
        second = _decision('second')
        second['baselineForecast']['settlement'] = 'bookmakerSettlement'
        events = [_decision('first'), first, correction, second, _outcome('second')]
        report = evaluate_journal(events, _protocol())
        self.assertEqual(report['observations'][0]['onPitchOutcome'], 'lost')
        self.assertEqual(report['observations'][0]['outcomeRecordsAfterCutoff'], 1)
        self.assertEqual(report['observations'][1]['baselineGateReason'], 'baseline-market-or-settlement-mismatch')
        self.assertEqual(report['pairedComparisons']['reference']['sampleSize'], 1)
        self.assertEqual(evaluate_journal(events)['observations'][0]['onPitchOutcome'], 'won')

    def test_clustered_uncertainty_and_protocol_coverage_gates(self):
        decisions = [_decision(f'd{i}') for i in range(20)]
        events = decisions + [_outcome(decision['id']) for decision in decisions]
        report = evaluate_journal(events, _protocol())
        comparison = report['pairedComparisons']['reference']
        self.assertEqual(comparison['sampleSize'], 20)
        self.assertLess(comparison['differences']['brier']['confidenceInterval']['upper'], 0)
        self.assertEqual(report['predictiveSuperiority'], 'supported-in-recorded-protocol-cohort')
        decisions[1]['fixture']['id'] = decisions[0]['fixture']['id']
        report = evaluate_journal(events, _protocol())
        self.assertEqual(report['pairedComparisons']['reference']['fixtureClusters'], 19)
        self.assertIn('fixture-cluster-minimum-unmet', report['superiorityGateReasons'])


class ProtocolTests(unittest.TestCase):
    def test_protocol_uses_registration_clock_and_artifacts_are_exclusive(self):
        spec = _protocol()
        del spec['registeredAt']
        now = datetime.now(timezone.utc)
        for field, delta in [('startsAt', 1), ('endsAt', 2), ('outcomeCutoff', 3)]:
            spec[field] = (now + timedelta(days=delta)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            path = register_protocol(tmp, spec)
            loaded = load_protocol(path)
            self.assertGreaterEqual(datetime.fromisoformat(loaded['registeredAt'].replace('Z', '+00:00')), now)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                register_protocol(tmp, {**spec, 'primaryMetric': 'log-loss'})
            with self.assertRaisesRegex(ValueError, 'assigned'):
                register_protocol(tmp, loaded)
            measurement = record_measurement(Path(tmp) / 'measurements', 'a', {'count': None})
            record_measurement(Path(tmp) / 'measurements', 'b', {'count': 5}, supersedes_id='a')
            self.assertIsNone(json.loads(measurement.read_text())['report']['count'])
            with self.assertRaisesRegex(ValueError, 'already exists'):
                record_measurement(measurement.parent, 'a', {'count': 8})


if __name__ == '__main__':
    unittest.main()
