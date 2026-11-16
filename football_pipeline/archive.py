"""Bridge a captured research run into the project's append-only journal."""
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

from scripts import journal
from .artifacts import read_json, save_json
from .request import fingerprint


def _time(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('run timestamps must include timezone')
    return parsed.astimezone(timezone.utc)


def archive_run(spec, bundle, manifest, project, journal_dir=None):
    if manifest.get('mode') != 'execute':
        raise ValueError('plans are not research decisions and cannot be archived as forecasts')
    if manifest.get('specHash') != fingerprint(spec) or manifest.get('evidenceHash') != fingerprint(bundle):
        raise ValueError('request/evidence do not match this run')
    project = Path(project).resolve()
    data = Path(journal_dir) if journal_dir else project / 'journal/data'
    (data / 'events').mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    if _time(manifest['finishedAt']) > now:
        raise ValueError('run finish time is in the future')
    signature = fingerprint(manifest)
    folder = project / 'research/pipeline-runs' / spec['id'] / signature[:16]
    for name, value in [('request', spec), ('evidence', bundle), ('manifest', manifest)]:
        save_json(folder / (name + '.json'), value)
    report = (folder / 'manifest.json').relative_to(project).as_posix()
    current = journal.load(data)
    counts = {'added': 0, 'unchanged': 0}

    def append(event):
        event['schemaVersion'] = 1
        event['recordedAt'] = current.get(event['id'], {}).get('recordedAt', datetime.now(timezone.utc).isoformat())
        with tempfile.TemporaryDirectory(prefix='football-archive-') as tmp:
            path = save_json(Path(tmp) / 'event.json', event)
            counts[journal.add(data, path)] += 1

    decisions = [*manifest.get('researchDecisions', []), *manifest.get('finalSelections', [])]
    if not decisions and manifest.get('screenedDecisions'):
        fixtures = {f['id']: f for f in bundle['fixtures']}
        screen_times = [c['finishedAt'] for c in manifest.get('calls', [])
                        if c.get('stage') == 'screen' and c.get('status') == 'completed' and c.get('finishedAt')]
        captured = max(screen_times, key=_time) if screen_times else manifest['finishedAt']
        decisions = [{**row, 'home': fixtures[row['fixtureId']]['home'], 'away': fixtures[row['fixtureId']]['away'],
                      'kickoffUtc': fixtures[row['fixtureId']]['kickoffUtc'], 'decidedAt': captured}
                     for row in manifest['screenedDecisions']]
    if len({r['directionId'] for r in decisions}) != len(decisions):
        raise ValueError('duplicate direction in research/final tables')
    ids = []
    for row in decisions:
        status = row['status']
        normalized = {'quote-pending': 'conditional', 'price-pass': 'pass', 'insufficient-evidence': 'pass',
                      'borderline': 'watch', 'survivor': 'candidate'}.get(status, status)
        if normalized not in journal.STATUSES:
            raise ValueError('unrecognized research status: ' + status)
        kickoff = _time(row['kickoffUtc'])
        captured = _time(row.get('decidedAt', manifest['finishedAt']))
        if captured > _time(manifest['finishedAt']):
            raise ValueError('decision time exceeds captured run finish')
        cohort = 'prospective' if now < kickoff else 'historical-import'
        ident = 'pipeline-' + fingerprint([manifest['runId'], row['directionId'], row])[:40]
        cohort = current.get(ident, {}).get('cohort', cohort)
        quote = row.get('verifiedQuote') or row.get('quote')
        market = row.get('market')
        if normalized == 'selected' and (manifest.get('status') != 'completed' or not quote or not market or captured >= kickoff):
            raise ValueError('selected row lacks completed pre-kickoff run/verified quote/market')
        append(dict(id=ident, type='decision', cohort=cohort,
                    matchDate=kickoff.astimezone(ZoneInfo(spec['timezone'])).date().isoformat(),
                    category=row['category'], fixture={'home': row['home']['name'], 'away': row['away']['name'], 'id': row['fixtureId']},
                    market={'rawLabel': row['direction'], 'resolved': bool(market), 'contract': market},
                    status=normalized, originalStatus=status,
                    source={'identity': manifest['runId'] + '#' + row['directionId'] + '#' + fingerprint(row), 'report': report},
                    originalTime={'value': captured.isoformat(), 'precision': 'exact', 'preKickoffEvidence': 'verified' if captured < kickoff else 'unknown'},
                    kickoff=row['kickoffUtc'], evidence={k: row.get(k) for k in ('observed','calculations','inference','sources')},
                    countercase={'reason': row['reason'], 'missing': row.get('missing', [])},
                    conditions='met' if normalized == 'selected' else row.get('gates', {'pending': row.get('missing', [])}),
                    odds=quote.get('decimalOdds') if quote else None, probability=None,
                    quoteObservation=quote, pipelineRunId=manifest['runId'],
                    note='Research record; placement and bookmaker settlement are not inferred.'))
        ids.append(ident)
    append(dict(id='pipeline-review-' + signature[:40], type='review', decisionIds=ids,
                note='Pipeline run archived with original decision statuses. ' +
                     ('No final selections.' if not manifest.get('finalSelections') else 'Final selections retain their observed terms.') +
                     ' Missing coverage and failed stages remain visible; no probabilities or actual wagers inferred.',
                matchDates=spec['dates'], categories=spec['categories'], source=report,
                finalSelectionCount=len(manifest.get('finalSelections', [])),
                coverage=manifest.get('coverage'), runStatus=manifest['status'],
                errors=manifest.get('errors', []), sourceErrors=manifest.get('sourceErrors', [])))
    journal.load(data)
    return {'writes': counts, 'report': report, 'decisionCount': len(ids), 'finalSelectionCount': len(manifest.get('finalSelections', []))}
