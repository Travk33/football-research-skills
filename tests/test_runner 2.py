import copy
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from football_pipeline.request import validate_request
from football_pipeline.runner import ExecutionResult, PipelineError, run_pipeline

NOW = datetime(2026, 11, 16, 12, tzinfo=timezone.utc)

def evidence():
    market = dict(family='winner', selection='home', line=None, period='full-time', teamId='1', playerId=None, rules='90 minutes', legs=[])
    stamp = NOW.isoformat()
    fixture = dict(id='10', home={'id':'1','name':'Home'}, away={'id':'2','name':'Away'},
                   kickoffUtc=(NOW + timedelta(hours=2)).isoformat(), competition={'id':'20','name':'League'}, status='scheduled',
                   sources=['https://evidence'], history={}, gaps=[], snapshot={'capturedAt':stamp,
                   'quotes':[dict(id='q', fixtureId='10', market=market, decimalOdds=2.0, bookmaker='Book', region='GB', observedAt=stamp, source='https://quote', ruleSource='https://rules')],
                   'lineup':dict(id='l', fixtureId='10', status='confirmed', observedAt=stamp, source='https://xi', homeStarters=[f'h{i}' for i in range(11)], awayStarters=[f'a{i}' for i in range(11)])})
    return dict(collectedAt=stamp, fixtures=[fixture], excluded=[], errors=[{'message':'provider unavailable'}], telemetry={'requests':1})

def spec(**limits):
    return validate_request(dict(schemaVersion=1, id='test', dates=['2026-11-16'], timezone='Europe/London', scope={'fixtureIds':['10']}, categories=['wins-btts'], limits=limits))

def analysis():
    return dict(observed=['A fact'], calculations=[], inference=['Judgment'], missing=[], sources=['https://evidence'])

class Executor:
    def __init__(self, survivor=True, fail=None, mutate=None):
        self.calls=[]; self.survivor=survivor; self.fail=fail; self.mutate=mutate
    def __call__(self, task, timeout):
        stage=task['stage']; self.calls.append(stage)
        if stage == self.fail:
            return ExecutionResult(error='deliberate failure')
        if stage == 'extraction':
            rows=[dict(fixtureId=i, **analysis()) for i in task['fixtureIds']]
        else:
            rows=[]
            for i in task['directions']:
                a=analysis(); row=dict(directionId=i, reason='Reason', **a)
                if stage == 'screen': row['status']='survivor' if self.survivor and i.endswith('home-win') else 'pass'
                if stage == 'review': row['status']='support'
                if stage == 'final':
                    quote=task['context']['snapshots']['10']['quotes'][0]
                    row.update(status='selected', market=copy.deepcopy(quote['market']), quoteId='q', lineupId='l', lineupRationale=None, lineupSources=[], gates=dict(evidence='met', contract='met', price='met', lineup='met'))
                    row['sources'] += ['https://quote','https://rules','https://xi']
                    if self.mutate: self.mutate(row)
                rows.append(row)
        return ExecutionResult(response={'rows':rows}, reported_model=task['requestedModel'], usage={'input_tokens':10})

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.clock=patch('football_pipeline.runner._now', return_value=NOW); self.clock.start(); self.addCleanup(self.clock.stop)
        self.bundle=evidence(); self.spec=spec()
    def run_pipeline(self, ex, **kwargs):
        return run_pipeline(self.spec, self.bundle, self.temp.name, execute=True, executor=ex, **kwargs)
    def test_full_flow_and_roles(self):
        ex=Executor(); result=self.run_pipeline(ex)
        self.assertEqual(result['status'],'completed'); self.assertEqual(ex.calls,['extraction','screen','deep','review','final'])
        self.assertEqual([c['role'] for c in result['calls']], ['retrieval','lead','lead','review','lead'])
        self.assertEqual(len(result['screenedDecisions']),3); self.assertEqual(len(result['researchDecisions']),2); self.assertEqual(len(result['finalSelections']),1)
        self.assertEqual(result['sourceErrors'],self.bundle['errors']); self.assertEqual(result['coverage']['directionsScreened'],3)
        self.run_pipeline(ex); self.assertEqual(len(ex.calls),5)
    def test_zero_survivors(self):
        ex=Executor(False); result=self.run_pipeline(ex)
        self.assertEqual(ex.calls,['extraction','screen']); self.assertEqual(result['finalSelections'],[]); self.assertEqual(len(result['researchDecisions']),3)
    def test_failure_and_resume_without_repeating_success(self):
        ex=Executor(fail='deep'); result=self.run_pipeline(ex)
        self.assertEqual(result['status'],'failed'); self.assertEqual(len(result['screenedDecisions']),3)
        ex.fail=None; result=self.run_pipeline(ex)
        self.assertEqual(result['status'],'completed'); self.assertEqual(ex.calls.count('screen'),1); self.assertEqual(ex.calls.count('deep'),2)
    def test_call_budget_never_exceeded(self):
        self.spec=spec(maxModelCalls=2); ex=Executor(); result=self.run_pipeline(ex)
        self.assertEqual(result['status'],'failed'); self.assertEqual(len(ex.calls),2); self.assertEqual(len(result['screenedDecisions']),3)
    def test_invalid_source_and_btts_no_fail_stage(self):
        for mutate in (lambda r:r['sources'].append('https://invented'), lambda r:r['market'].update(family='btts', selection='no', teamId=None)):
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                result=run_pipeline(self.spec,self.bundle,directory,execute=True,executor=Executor(mutate=mutate))
                self.assertEqual(result['status'],'failed'); self.assertEqual(result['finalSelections'],[])
    def test_invalid_quote_and_lineup_do_not_select(self):
        for change in ('quote','lineup'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                bundle=copy.deepcopy(self.bundle)
                if change=='quote': bundle['fixtures'][0]['snapshot']['quotes'][0]['decimalOdds']=1
                else: bundle['fixtures'][0]['snapshot']['lineup']['status']='predicted'
                result=run_pipeline(self.spec,bundle,directory,execute=True,executor=Executor())
                self.assertEqual(result['status'],'completed'); self.assertEqual(result['finalSelections'],[])
                self.assertTrue(any(row.get('proposedStatus')=='selected' for row in result['researchDecisions']))
    def test_lineup_exception_requires_justification_and_cited_source(self):
        def exception(row):
            row.update(lineupId=None, lineupRationale='XI changes do not materially alter this team-market case', lineupSources=['https://evidence'])
            row['gates']['lineup']='not-required'
        self.bundle['fixtures'][0]['snapshot']['lineup']['status']='predicted'
        result=self.run_pipeline(Executor(mutate=exception))
        self.assertEqual(len(result['finalSelections']),1)
        def no_justification(row):
            exception(row); row['lineupRationale']=None
        with tempfile.TemporaryDirectory() as directory:
            result=run_pipeline(self.spec,self.bundle,directory,execute=True,executor=Executor(mutate=no_justification))
            self.assertEqual(result['finalSelections'],[])
    def test_plan_has_no_calls_and_kickoff_during_execution_fails(self):
        ex=Executor(); plan=run_pipeline(self.spec,self.bundle,self.temp.name,executor=ex)
        self.assertEqual(plan['status'],'planned'); self.assertEqual(ex.calls,[])
        def reaches_kickoff(task, timeout):
            self.clock.stop()
            self.clock=patch('football_pipeline.runner._now',return_value=NOW+timedelta(hours=3)); self.clock.start()
            return ex(task,timeout)
        result=run_pipeline(self.spec,self.bundle,self.temp.name,execute=True,executor=reaches_kickoff)
        self.assertEqual(result['status'],'failed'); self.assertEqual(result['finalSelections'],[])
        self.assertIn('kickoff',result['errors'][-1])
    def test_stage_batch_sizes_preserve_fixture_and_direction_coverage(self):
        bundle=copy.deepcopy(self.bundle)
        for fixture_id in ('11', '12', '13', '14'):
            fixture=copy.deepcopy(bundle['fixtures'][0]); fixture['id']=fixture_id
            bundle['fixtures'].append(fixture)
        request=validate_request(dict(schemaVersion=1, id='batch', dates=['2026-11-16'], timezone='Europe/London',
            scope={'fixtureIds':['10','11','12','13','14']}, categories=['wins-btts'],
            limits={'batchSize':2,'leadBatchSize':3,'deepBatchSize':2,'reviewBatchSize':4}))
        tasks=[]
        def executor(task, timeout):
            tasks.append(task)
            if task['stage']=='extraction':
                return {'rows':[dict(fixtureId=i, **analysis()) for i in task['fixtureIds']]}
            rows=[]
            for direction in task['directions']:
                row=dict(directionId=direction, reason='Reason', **analysis())
                if task['stage']=='screen': row['status']='survivor' if direction.endswith('home-win') else 'pass'
                if task['stage']=='review': row['status']='support'
                if task['stage']=='final':
                    row.update(status='pass', market=None, quoteId=None, lineupId=None, lineupRationale=None,
                               lineupSources=[], gates=dict(evidence='pending',contract='pending',price='pending',lineup='pending'))
                rows.append(row)
            return {'rows':rows}
        result=run_pipeline(request,bundle,self.temp.name,execute=True,executor=executor)
        self.assertEqual(result['status'],'completed')
        self.assertEqual({stage:sum(t['stage']==stage for t in tasks) for stage in ('extraction','screen','deep','review','final')},
                         {'extraction':3,'screen':2,'deep':3,'review':2,'final':2})
        self.assertEqual(len(result['screenedDecisions']),15)
        self.assertEqual(len(result['researchDecisions']),15)
        self.assertTrue(all(row['decidedAt'] and 'market' in row and 'gates' in row for row in result['researchDecisions']))
        for task in tasks:
            self.assertEqual({f['id'] for f in task['context']['fixtures']},set(task['fixtureIds']))
            self.assertTrue(all(i.split('/')[0] in task['fixtureIds'] for i in task['directions']))
        plan=run_pipeline(request,bundle,self.temp.name)
        self.assertEqual(plan['maximumPlannedModelCalls'],12)
    def test_replay_after_kickoff_is_archive_and_changed_fixture_rejected(self):
        ex=Executor(); initial=self.run_pipeline(ex)
        with patch('football_pipeline.runner._now',return_value=NOW+timedelta(hours=3)):
            replay=self.run_pipeline(ex)
        self.assertEqual(replay['status'],'archived'); self.assertEqual(replay['finalSelections'],[]); self.assertEqual(len(replay['archivedFinalSelections']),1)
        changed=copy.deepcopy(self.bundle); changed['fixtures'][0]['kickoffUtc']=(NOW+timedelta(hours=4)).isoformat()
        with self.assertRaises(PipelineError): run_pipeline(self.spec,changed,self.temp.name,execute=True,executor=ex)
        self.assertEqual(initial['status'],'completed')

if __name__ == '__main__': unittest.main()
