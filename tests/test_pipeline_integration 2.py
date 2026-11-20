from contextlib import redirect_stdout
import copy
from datetime import datetime, timedelta, timezone
import io
from pathlib import Path
import tempfile
import unittest

from football_pipeline.archive import archive_run
from football_pipeline.artifacts import read_json, save_json
from football_pipeline.cli import main
from football_pipeline.enrichment import merge_evidence
from football_pipeline.request import fingerprint, validate_request
from football_pipeline.runner import run_pipeline
from scripts import journal
from tests.test_runner import Executor, evidence


def inputs():
    now=datetime.now(timezone.utc)-timedelta(seconds=1)
    bundle=evidence(); bundle['collectedAt']=now.isoformat()
    fixture=bundle['fixtures'][0]; fixture['kickoffUtc']=(now+timedelta(days=1)).isoformat()
    snapshot=fixture['snapshot']; snapshot['capturedAt']=now.isoformat()
    snapshot['quotes'][0]['observedAt']=now.isoformat(); snapshot['lineup']['observedAt']=now.isoformat()
    spec=validate_request({'schemaVersion':1,'id':'integration','dates':[fixture['kickoffUtc'][:10]],
                          'timezone':'UTC','scope':{'fixtureIds':['10']},'categories':['wins-btts']})
    return spec,bundle


class IntegrationTests(unittest.TestCase):
    def test_execute_archive_and_replay_preserve_all_directions(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec,bundle=inputs(); manifest=run_pipeline(spec,bundle,Path(tmp)/'run',True,Executor())
            archived=archive_run(spec,bundle,manifest,tmp)
            self.assertEqual(archived['decisionCount'],3)
            events=journal.load(Path(tmp)/'journal/data')
            decisions=[x for x in events.values() if x['type']=='decision']
            self.assertEqual({x['cohort'] for x in decisions},{'prospective'})
            self.assertEqual(sum(x['status']=='selected' for x in decisions),1)
            replay=archive_run(spec,bundle,manifest,tmp)
            self.assertEqual(replay['writes'],{'added':0,'unchanged':4})
            self.assertTrue((Path(tmp)/archived['report']).exists())

    def test_failed_deep_stage_keeps_completed_screen_in_journal(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec,bundle=inputs(); manifest=run_pipeline(spec,bundle,Path(tmp)/'run',True,Executor(fail='deep'))
            self.assertEqual(manifest['status'],'failed')
            archived=archive_run(spec,bundle,manifest,tmp)
            self.assertEqual(archived['decisionCount'],3)
            self.assertEqual(archived['finalSelectionCount'],0)

    def test_plan_is_not_archived_and_artifacts_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec,bundle=inputs(); plan=run_pipeline(spec,bundle,Path(tmp)/'run')
            with self.assertRaises(ValueError): archive_run(spec,bundle,plan,tmp)
            target=Path(tmp)/'data.json'; save_json(target,{'original':True})
            with self.assertRaises(ValueError): save_json(target,{'original':False})
            self.assertEqual(read_json(target),{'original':True})

    def test_enrichment_has_lineage_and_does_not_refresh_old_sources(self):
        _,bundle=inputs(); original=copy.deepcopy(bundle)
        stamp=datetime.now(timezone.utc).isoformat()
        supplement={'evidenceHash':fingerprint(bundle),'fixtures':[{'id':'10','news':[
            {'fixtureId':'10','observedAt':stamp,'source':'https://club.example/news','claim':'Example fact'}]}]}
        updated=merge_evidence(bundle,supplement)
        self.assertEqual(bundle,original)
        self.assertEqual(updated['previousEvidenceHash'],fingerprint(bundle))
        self.assertGreaterEqual(updated['collectedAt'],stamp)
        self.assertEqual(updated['fixtures'][0]['snapshot']['quotes'][0]['observedAt'],original['collectedAt'])
        bad=copy.deepcopy(supplement); bad['fixtures'][0]['id']='999'
        with self.assertRaises(ValueError): merge_evidence(bundle,bad)

    def test_cli_init_plan_and_usage(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            spec,bundle=inputs(); request=Path(tmp)/'request.json'; evidence_path=Path(tmp)/'evidence.json'
            save_json(request,spec); save_json(evidence_path,bundle)
            self.assertEqual(main(['run','--request',str(request),'--evidence',str(evidence_path),'--output-dir',str(Path(tmp)/'run')]),0)
            manifest=Path(tmp)/'run/plan/manifest.json'
            self.assertEqual(read_json(manifest)['calls'],[])
            self.assertEqual(main(['usage','--manifest',str(manifest)]),0)


if __name__=='__main__': unittest.main()
