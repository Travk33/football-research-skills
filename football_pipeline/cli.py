"""Command-line entrypoints for scoped research and honest measurement."""
import argparse
from pathlib import Path
import sys

from .artifacts import read_json, save_json
from .request import validate_request

ROOT = Path(__file__).resolve().parents[1]


def _emit(value):
    import json
    print(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))


def parser():
    p = argparse.ArgumentParser(description='Variable-scope football research; no betting transactions.')
    sub = p.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='Create an explicit request; provider IDs come from discover.')
    init.add_argument('--id', required=True)
    init.add_argument('--date', action='append', required=True)
    init.add_argument('--timezone', default='Europe/London')
    for name in ('competition-id', 'fixture-id', 'team-id', 'builder-fixture-id'):
        init.add_argument('--' + name, action='append', default=[])
    init.add_argument('--category', action='append', choices=['wins-btts','other-markets','bet-builders'])
    init.add_argument('--all-competitions', action='store_true')
    init.add_argument('--gender', choices=['male','female'])
    init.add_argument('--history', type=int, default=8)
    init.add_argument('--details', type=int, default=3)
    init.add_argument('--out', required=True)

    discover = sub.add_parser('discover', help='List scheduled fixtures and their IDs without model calls.')
    discover.add_argument('--date', action='append', required=True)
    discover.add_argument('--timezone', default='Europe/London')
    discover.add_argument('--cache', default=str(ROOT / '.cache/football-pipeline'))
    discover.add_argument('--max-requests', type=int, default=12)
    discover.add_argument('--out')

    collect = sub.add_parser('collect', help='Collect/cache shared evidence for the explicit request.')
    collect.add_argument('--request', required=True)
    collect.add_argument('--cache', default=str(ROOT / '.cache/football-pipeline'))
    collect.add_argument('--out', required=True)

    merge = sub.add_parser('enrich', help='Merge sourced news/price/rule snapshots into a new evidence artifact.')
    merge.add_argument('--evidence', required=True)
    merge.add_argument('--supplement', required=True)
    merge.add_argument('--out', required=True)

    run = sub.add_parser('run', help='Plan by default; --execute makes bounded explicitly routed Codex calls.')
    for name in ('request','evidence','output-dir'):
        run.add_argument('--' + name, required=True)
    run.add_argument('--execute', action='store_true')
    run.add_argument('--project', default=str(ROOT))
    run.add_argument('--no-archive', action='store_true', help='For smoke tests only; normal research is journaled.')

    archive = sub.add_parser('archive', help='Append a captured execute run to the journal.')
    for name in ('request','evidence','manifest'):
        archive.add_argument('--' + name, required=True)
    archive.add_argument('--project', default=str(ROOT))

    usage = sub.add_parser('usage', help='Report observed calls/tokens/cache and optional API-rate estimates.')
    usage.add_argument('--manifest', required=True)
    usage.add_argument('--rates')
    usage.add_argument('--out')

    compare = sub.add_parser('compare-costs', help='Compare complete matching work from two distinct executions.')
    compare.add_argument('--baseline', required=True)
    compare.add_argument('--candidate', required=True)
    compare.add_argument('--rates')
    compare.add_argument('--out')

    evaluate = sub.add_parser('evaluate', help='Evaluate genuinely prospective recorded forecasts.')
    evaluate.add_argument('--journal', default=str(ROOT / 'journal/data'))
    evaluate.add_argument('--protocol')
    evaluate.add_argument('--out')

    register = sub.add_parser('register-protocol', help='Register a future evaluation plan without backdating.')
    register.add_argument('--spec', required=True)
    register.add_argument('--directory', default=str(ROOT / 'journal/protocols'))
    measurement = sub.add_parser('record-measurement', help='Preserve an immutable usage or evaluation report.')
    measurement.add_argument('--id', required=True)
    measurement.add_argument('--report', required=True)
    measurement.add_argument('--directory', default=str(ROOT / 'journal/measurements'))
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return dispatch(args)
    except (ValueError, OSError, KeyError) as exc:
        print('pipeline: ' + str(exc), file=sys.stderr)
        return 2


def dispatch(args):
    command = args.command
    if command == 'init':
        scope = {'competitionIds': args.competition_id, 'fixtureIds': args.fixture_id,
                 'teamIds': args.team_id, 'allCompetitions': args.all_competitions}
        if args.gender: scope['gender'] = args.gender
        spec = validate_request({'schemaVersion':1, 'id':args.id, 'dates':args.date, 'timezone':args.timezone,
                                 'scope':scope, 'categories':args.category or ['wins-btts','other-markets'],
                                 'historyMatches':args.history, 'historyDetails':args.details,
                                 'builderFixtureIds':args.builder_fixture_id})
        _emit({'request':str(save_json(args.out,spec)), 'routing':spec['routing'], 'limits':spec['limits']})
    elif command in {'collect','discover'}:
        from .collector import Collector
        if command == 'collect':
            spec = validate_request(read_json(args.request))
        else:
            spec = validate_request({'schemaVersion':1,'id':'discovery','dates':args.date,'timezone':args.timezone,
                                     'scope':{'allCompetitions':True},'categories':['wins-btts'],
                                     'historyMatches':0,'historyDetails':0,'includeTargetDetails':False,
                                     'limits':{'maxRequests':args.max_requests}})
        collector = Collector(args.cache,max_requests=spec['limits']['maxRequests'],timeout=min(20,spec['limits']['timeoutSeconds']))
        bundle = collector.collect(spec)
        if args.out: save_json(args.out,bundle)
        _emit({'evidence':args.out,'fixtures':[{k:f[k] for k in ('id','home','away','kickoffUtc','competition')} for f in bundle['fixtures']],
               'excludedCount':len(bundle['excluded']),'errors':bundle['errors'],'telemetry':bundle['telemetry']})
        return 0 if not bundle['errors'] else 2
    elif command == 'enrich':
        from .enrichment import merge_evidence
        bundle = merge_evidence(read_json(args.evidence),read_json(args.supplement))
        _emit({'evidence':str(save_json(args.out,bundle)), 'fixtureCount':len(bundle['fixtures'])})
    elif command == 'run':
        from .runner import run_pipeline
        from .archive import archive_run
        from .evaluation import usage_report
        spec = validate_request(read_json(args.request)); bundle = read_json(args.evidence)
        manifest = run_pipeline(spec,bundle,args.output_dir,execute=args.execute)
        artifact = Path(args.output_dir)/('manifest.json' if args.execute else 'plan/manifest.json')
        result = {'status':manifest['status'],'manifest':str(artifact),'coverage':manifest.get('coverage'),
                  'finalSelectionCount':len(manifest.get('finalSelections',[])), 'errors':manifest.get('errors',[]),
                  'usage':usage_report(manifest)}
        if args.execute and not args.no_archive:
            # Archived replay is read-only; retain the original complete manifest for a historical import.
            recorded = read_json(artifact) if manifest['status'] == 'archived' else manifest
            result['journal'] = archive_run(spec,bundle,recorded,args.project)
        _emit(result)
        return 0 if manifest['status'] in {'planned','completed','archived'} else 2
    elif command == 'archive':
        from .archive import archive_run
        _emit(archive_run(validate_request(read_json(args.request)),read_json(args.evidence),read_json(args.manifest),args.project))
    elif command in {'usage','compare-costs'}:
        from .evaluation import usage_report, compare_costs
        rates = read_json(args.rates) if args.rates else None
        if command == 'usage':
            report = usage_report(read_json(args.manifest),rates)
        else:
            records = [read_json(path) for path in (args.baseline,args.candidate)]
            reports = [r if r.get('kind') == 'usage-report' else usage_report(r,rates) for r in records]
            report = compare_costs(*reports)
        if args.out: save_json(args.out,report)
        _emit(report)
    elif command == 'evaluate':
        from scripts import journal
        from .evaluation import evaluate_journal
        from .protocol import load_protocol
        report = evaluate_journal(journal.load(Path(args.journal)),load_protocol(args.protocol) if args.protocol else None)
        if args.out: save_json(args.out,report)
        _emit(report)
    elif command == 'register-protocol':
        from .protocol import register_protocol
        _emit({'protocol':str(register_protocol(args.directory,read_json(args.spec)))})
    elif command == 'record-measurement':
        from .protocol import record_measurement
        _emit({'measurement':str(record_measurement(args.directory,args.id,read_json(args.report)))})
    return 0
