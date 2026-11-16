import copy
import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('journal', Path(__file__).resolve().parents[1] / 'scripts/journal.py')
journal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(journal)


def decision():
    return {'schemaVersion': 1, 'id': 'd1', 'type': 'decision', 'recordedAt': '2026-11-15T12:00:00Z', 'cohort': 'historical-import', 'matchDate': '2026-11-14', 'category': 'wins-btts', 'fixture': {'home': 'A', 'away': 'B'}, 'market': {'rawLabel': 'A win', 'resolved': True}, 'status': 'pass', 'source': {'identity': 'report-1-entry-1', 'report': 'report'}, 'originalTime': {'value': '2026-11-14T12:00:00Z', 'precision': 'exact', 'preKickoffEvidence': 'claimed'}, 'kickoff': '2026-11-14T15:00:00Z', 'evidence': None, 'countercase': None, 'conditions': None, 'odds': None, 'probability': None}


class JournalTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name) / 'data'
        (self.data / 'events').mkdir(parents=True)
        self.input = Path(self.temp.name) / 'input.json'
    def tearDown(self): self.temp.cleanup()
    def add(self, obj, now=None):
        self.input.write_text(json.dumps(obj))
        return journal.add(self.data, self.input, now or (journal.timestamp(obj['recordedAt'], 'recordedAt') + dt.timedelta(seconds=1)))
    def test_idempotence_and_duplicate_identity(self):
        d = decision()
        self.assertEqual(self.add(d), 'added')
        self.assertEqual(self.add(d), 'unchanged')
        changed = dict(d, status='selected')
        with self.assertRaisesRegex(ValueError, 'different content'): self.add(changed)
        with self.assertRaisesRegex(ValueError, 'duplicate source'): self.add(dict(d, id='d2'))
        self.assertEqual(journal.load(self.data)['d1']['status'], 'pass')
    def test_revision_cannot_promote_after_kickoff(self):
        self.add(decision())
        revision = {'schemaVersion': 1, 'id': 'r1', 'type': 'status_revision', 'recordedAt': '2026-11-15T12:00:00Z', 'decisionId': 'd1', 'status': 'selected', 'effectiveAt': '2026-11-14T15:00:00Z', 'reason': 'late'}
        with self.assertRaisesRegex(ValueError, 'kickoff'): self.add(revision)
        revision.update(status='watch', effectiveAt='2026-11-14T14:00:00Z')
        self.add(revision)
        self.assertEqual(journal.load(self.data)['d1']['status'], 'pass')
        self.assertEqual(journal.summary(journal.load(self.data))['historical-import']['statuses'], {'pass': 1})
    def test_outcomes_only_count_selected_and_missing_stays_pending(self):
        d = decision(); self.add(d)
        selected = copy.deepcopy(d); selected.update(id='d2', status='selected'); selected['source']['identity'] = 'another'; self.add(selected)
        outcome = {'schemaVersion': 1, 'id': 'o1', 'type': 'outcome', 'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'd1', 'evidenceLevel': 'documented', 'onPitchOutcome': 'won', 'ruleBasedOutcome': 'unknown', 'bookmakerSettlement': 'unknown', 'sources': ['saved report']}
        self.add(outcome)
        s = journal.summary(journal.load(self.data))['historical-import']
        self.assertEqual(s['selectedOnPitchOutcomes'], {'pending': 1})
        self.assertIsNone(s['binaryHitRate'])
        self.assertEqual(s['binaryResolved'], 0)
        outcome.update(id='o2', decisionId='d2', bookmakerSettlement='won')
        with self.assertRaisesRegex(ValueError, 'receiptEvidence'): self.add(outcome)
    def test_directional_outcomes_preserve_original_and_effective_status(self):
        d = decision(); d['status'] = 'conditional'; self.add(d)
        revision = {'schemaVersion': 1, 'id': 'r1', 'type': 'status_revision', 'recordedAt': '2026-11-15T12:00:00Z', 'decisionId': 'd1', 'status': 'watch', 'effectiveAt': '2026-11-14T14:00:00Z', 'reason': 'conditions unclear'}
        self.add(revision)
        outcome = {'schemaVersion': 1, 'id': 'o1', 'type': 'outcome', 'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'd1', 'evidenceLevel': 'documented', 'onPitchOutcome': 'lost', 'ruleBasedOutcome': 'unknown', 'bookmakerSettlement': 'unknown', 'sources': ['saved report']}
        self.add(outcome)
        s = journal.summary(journal.load(self.data))['historical-import']
        self.assertEqual(s['directionalOnPitchOutcomes']['wins-btts']['conditional']['conditional'], {'lost': 1})
        self.assertEqual(s['selectedOnPitchOutcomes'], {})
        self.assertIsNone(s['binaryHitRate'])

    def test_prospective_gate_and_broken_reference(self):
        d = decision(); d.update(cohort='prospective', status='selected', recordedAt='2026-11-14T12:01:00Z')
        with self.assertRaisesRegex(ValueError, 'prospective selection'): self.add(d, dt.datetime(2026, 11, 14, 12, 2, tzinfo=dt.timezone.utc))
        d.update(conditions='met', odds=2.0); d['originalTime']['preKickoffEvidence'] = 'verified'
        self.add(d, dt.datetime(2026, 11, 14, 12, 2, tzinfo=dt.timezone.utc))
        o = {'schemaVersion': 1, 'id': 'o1', 'type': 'outcome', 'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'missing', 'evidenceLevel': 'pending', 'onPitchOutcome': 'unknown', 'ruleBasedOutcome': 'unknown', 'bookmakerSettlement': 'unknown', 'sources': ['saved report']}
        with self.assertRaisesRegex(ValueError, 'missing decision'): self.add(o)
    def test_late_prospective_capture_and_backdated_demotion(self):
        d = decision(); d.update(cohort='prospective', status='selected', recordedAt='2026-11-14T12:01:00Z', conditions='met', odds=2.0)
        d['originalTime']['preKickoffEvidence'] = 'verified'
        with self.assertRaisesRegex(ValueError, 'appended before'): self.add(d, dt.datetime(2026, 11, 16, 13, tzinfo=dt.timezone.utc))
        self.add(d, dt.datetime(2026, 11, 14, 12, 2, tzinfo=dt.timezone.utc))
        rev = {'schemaVersion': 1, 'id': 'r1', 'type': 'status_revision', 'recordedAt': '2026-11-14T14:00:00Z', 'decisionId': 'd1', 'status': 'pass', 'effectiveAt': '2026-11-14T14:00:00Z', 'reason': 'backdated'}
        self.add(rev, dt.datetime(2026, 11, 16, 13, tzinfo=dt.timezone.utc))
        self.assertEqual(journal.summary(journal.load(self.data))['prospective']['selectedTotal'], 1)
        rev['id'] = 'r2'
        rev['recordedAt'] = '2026-11-14T12:01:00Z'
        rev['effectiveAt'] = '2026-11-14T12:01:00Z'
        with self.assertRaisesRegex(ValueError, 'precedes parent'): self.add(rev, dt.datetime(2026, 11, 14, 12, 1, tzinfo=dt.timezone.utc))
        self.assertEqual(self.add(d), 'unchanged')

    def test_agreeing_and_disputed_outcome_heads(self):
        d = decision(); d['status'] = 'selected'; self.add(d)
        o = {'schemaVersion': 1, 'id': 'o1', 'type': 'outcome', 'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'd1', 'evidenceLevel': 'verified', 'onPitchOutcome': 'lost', 'ruleBasedOutcome': 'unknown', 'bookmakerSettlement': 'unknown', 'sources': ['saved report']}
        self.add(o); self.add(dict(o, id='o2'))
        self.assertEqual(journal.summary(journal.load(self.data))['historical-import']['selectedOnPitchOutcomes'], {'lost': 1})
        self.add(dict(o, id='o3', onPitchOutcome='won'))
        self.assertEqual(journal.summary(journal.load(self.data))['historical-import']['selectedOnPitchOutcomes'], {'needs-review': 1})

    def test_appended_at_is_tool_controlled_and_published_atomically(self):
        d = decision(); d['appendedAt'] = '2026-11-14T12:00:00Z'
        with self.assertRaisesRegex(ValueError, 'assigned by the journal'): self.add(d)
        del d['appendedAt']; self.add(d)
        persisted = json.loads((self.data / 'events' / 'd1.json').read_text())
        self.assertEqual(persisted['appendedAt'], '2026-11-15T12:00:01Z')
        self.assertEqual(self.add(persisted), 'unchanged')
        self.assertEqual([p.name for p in (self.data / 'events').iterdir()], ['d1.json'])
        other = decision(); other['id'] = 'd2'; other['source']['identity'] = 'other'
        with mock.patch.object(journal.os, 'link', side_effect=FileExistsError):
            with self.assertRaisesRegex(ValueError, 'reload and retry'): self.add(other)
        self.assertEqual([p.name for p in (self.data / 'events').iterdir()], ['d1.json'])

    def test_outcome_chronology_sources_and_supersedes_type(self):
        self.add(decision())
        o = {'schemaVersion': 1, 'id': 'o1', 'type': 'outcome', 'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'd1', 'evidenceLevel': 'verified', 'onPitchOutcome': 'lost', 'ruleBasedOutcome': 'unknown', 'bookmakerSettlement': 'unknown', 'sources': ['result report']}
        with self.assertRaisesRegex(ValueError, 'requires sources'): self.add(dict(o, sources=[]))
        with self.assertRaisesRegex(ValueError, 'invalid supersedesId'): self.add(dict(o, supersedesId=[]))
        with self.assertRaisesRegex(ValueError, 'before parent capture'): self.add(dict(o, recordedAt='2026-11-15T11:00:00Z'))
        self.add(o)
        d = decision(); d.update(id='d2', kickoff='2026-11-20T15:00:00Z'); d['source']['identity'] = 'other'
        self.add(d)
        with self.assertRaisesRegex(ValueError, 'after kickoff'): self.add(dict(o, id='o2', decisionId='d2'))

    def test_outcome_requires_meaningful_sources_and_receipt_note(self):
        self.add(decision())
        outcome = {
            'schemaVersion': 1, 'id': 'o1', 'type': 'outcome',
            'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'd1',
            'evidenceLevel': 'verified', 'onPitchOutcome': 'won',
            'ruleBasedOutcome': 'won', 'bookmakerSettlement': 'unknown',
            'sources': [{'path': 'saved-results.json', 'detail': 'Final score'}],
        }
        for invalid_sources in ([None], ['  '], [{}], [{'url': ' '}], [True]):
            with self.subTest(sources=invalid_sources):
                with self.assertRaisesRegex(ValueError, 'nonblank references'):
                    self.add(dict(outcome, sources=invalid_sources))
        for invalid_receipt in (None, True, '  '):
            with self.subTest(receipt=invalid_receipt):
                with self.assertRaisesRegex(ValueError, 'nonblank note'):
                    self.add(dict(outcome, bookmakerSettlement='won', receiptEvidence=invalid_receipt))
        self.assertEqual(self.add(dict(outcome, bookmakerSettlement='won', receiptEvidence='Operator marked the market as won.')), 'added')

    def test_resolved_outcome_without_kickoff_requires_historical_evidence(self):
        self.add(dict(decision(), kickoff=None))
        demo = dict(decision(), id='demo', cohort='demo', kickoff=None, source={'identity': 'demo-source', 'report': None})
        self.add(demo)
        outcome = {
            'schemaVersion': 1, 'id': 'o1', 'type': 'outcome',
            'recordedAt': '2026-11-16T12:00:00Z', 'decisionId': 'd1',
            'evidenceLevel': 'documented', 'onPitchOutcome': 'lost',
            'ruleBasedOutcome': 'unknown', 'bookmakerSettlement': 'unknown',
            'sources': ['saved result report'],
        }
        with self.assertRaisesRegex(ValueError, 'documented or verified historical result'):
            self.add(dict(outcome, evidenceLevel='pending'))
        with self.assertRaisesRegex(ValueError, 'documented or verified historical result'):
            self.add(dict(outcome, decisionId='demo'))
        self.assertEqual(self.add(outcome), 'added')
        snapshot = journal.summary(journal.load(self.data))
        self.assertEqual(snapshot['historical-import']['directionalOnPitchOutcomes']['wins-btts']['pass']['pass'], {'lost': 1})
        self.assertEqual(snapshot['prospective']['decisions'], 0)

    def test_invalid_id_and_corrupt_store_fail(self):
        d = decision(); d['id'] = '../escape'
        with self.assertRaisesRegex(ValueError, 'invalid id'): self.add(d)
        (self.data / 'events' / 'bad.json').write_text('{')
        with self.assertRaises(ValueError): journal.load(self.data)

if __name__ == '__main__': unittest.main()
