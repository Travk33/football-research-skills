#!/usr/bin/env python3
"""Small append-only football decision journal; all operations use stdlib."""
import argparse
import datetime as dt
import fcntl
import json
import math
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'journal' / 'data'
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')
STATUSES = {'candidate', 'conditional', 'watch', 'reserve', 'pass', 'selected'}
OUTCOMES = {'won', 'lost', 'push', 'void', 'half-won', 'half-lost', 'pending', 'unknown', 'needs-review'}
TYPES = {'decision', 'status_revision', 'outcome', 'review', 'method_change'}


def timestamp(value, label, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise ValueError(f'{label} must be an ISO timestamp with timezone')
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        raise ValueError(f'{label} must be an ISO timestamp with timezone') from None


def require(obj, fields):
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ValueError('missing fields: ' + ', '.join(missing))


def identifier(value, label):
    if not isinstance(value, str) or not ID.fullmatch(value) or value in {'.', '..'}:
        raise ValueError(f'invalid {label}')


def nonblank_text(value):
    return isinstance(value, str) and bool(value.strip())


def source_reference(value):
    if isinstance(value, dict):
        return any(nonblank_text(value.get(key)) for key in ('url', 'path', 'reference'))
    return nonblank_text(value)


def finite_numbers(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('non-finite number')
    if isinstance(value, dict):
        for item in value.values(): finite_numbers(item)
    elif isinstance(value, list):
        for item in value: finite_numbers(item)


def check_event(e):
    if not isinstance(e, dict): raise ValueError('event must be an object')
    require(e, ['schemaVersion', 'id', 'type', 'recordedAt', 'appendedAt'])
    if type(e['schemaVersion']) is not int or e['schemaVersion'] != 1: raise ValueError('unsupported schemaVersion')
    identifier(e['id'], 'id')
    if e['type'] not in TYPES: raise ValueError('invalid type')
    recorded = timestamp(e['recordedAt'], 'recordedAt')
    appended = timestamp(e['appendedAt'], 'appendedAt')
    if recorded > appended: raise ValueError('recordedAt after appendedAt')
    finite_numbers(e)
    typ = e['type']
    if typ == 'decision':
        require(e, ['cohort', 'matchDate', 'category', 'fixture', 'market', 'status', 'source', 'originalTime', 'kickoff', 'evidence', 'countercase', 'conditions', 'odds', 'probability'])
        if e['cohort'] not in {'prospective', 'historical-import', 'demo'}: raise ValueError('invalid cohort')
        try: dt.date.fromisoformat(e['matchDate'])
        except (ValueError, TypeError): raise ValueError('invalid matchDate') from None
        if e['category'] not in {'wins-btts', 'other-markets', 'bet-builders'}: raise ValueError('invalid category')
        if e['status'] not in STATUSES: raise ValueError('invalid status')
        if not isinstance(e['fixture'], dict) or not isinstance(e['market'], dict): raise ValueError('fixture and market must be objects')
        require(e['fixture'], ['home', 'away'])
        require(e['market'], ['rawLabel', 'resolved'])
        if not isinstance(e['market']['resolved'], bool): raise ValueError('market.resolved must be boolean')
        if not isinstance(e['source'], dict): raise ValueError('source must be an object')
        require(e['source'], ['identity', 'report'])
        if not nonblank_text(e['source']['identity']): raise ValueError('source.identity is required for duplicate detection')
        if not isinstance(e['originalTime'], dict): raise ValueError('originalTime must be an object')
        require(e['originalTime'], ['value', 'precision', 'preKickoffEvidence'])
        if e['originalTime']['precision'] not in {'exact', 'approximate', 'date-only', 'unknown'}: raise ValueError('invalid originalTime precision')
        if e['originalTime']['preKickoffEvidence'] not in {'verified', 'claimed', 'unknown'}: raise ValueError('invalid preKickoffEvidence')
        original = timestamp(e['originalTime']['value'], 'originalTime.value', True)
        if e['originalTime']['precision'] == 'exact' and original is None: raise ValueError('exact originalTime requires a timestamp')
        kickoff = timestamp(e['kickoff'], 'kickoff', True)
        if original and original > timestamp(e['recordedAt'], 'recordedAt'): raise ValueError('originalTime after recordedAt')
        if e['odds'] is not None and (isinstance(e['odds'], bool) or not isinstance(e['odds'], (int, float)) or e['odds'] <= 1): raise ValueError('odds must be null or decimal odds > 1')
        if e['probability'] is not None and (isinstance(e['probability'], bool) or not isinstance(e['probability'], (int, float)) or not 0 <= e['probability'] <= 1): raise ValueError('probability must be null or between 0 and 1')
        if e['status'] == 'selected' and original and kickoff and original >= kickoff: raise ValueError('decision selected at or after kickoff')
        if e['cohort'] == 'prospective' and (not kickoff or appended >= kickoff): raise ValueError('prospective decision must be appended before known kickoff')
        if e['cohort'] == 'prospective' and e['status'] == 'selected':
            if not (original and kickoff and original < kickoff and e['originalTime']['precision'] == 'exact' and e['originalTime']['preKickoffEvidence'] == 'verified' and e['market']['resolved'] and e['odds'] is not None and e['conditions'] == 'met' and timestamp(e['recordedAt'], 'recordedAt') < kickoff):
                raise ValueError('prospective selection requires verified pre-kickoff capture, resolved market, price and met conditions')
    elif typ in {'status_revision', 'outcome'}:
        require(e, ['decisionId'])
        identifier(e['decisionId'], 'decisionId')
        if typ == 'status_revision':
            require(e, ['status', 'effectiveAt', 'reason'])
            if e['status'] not in STATUSES: raise ValueError('invalid status')
            timestamp(e['effectiveAt'], 'effectiveAt')
        else:
            require(e, ['evidenceLevel', 'onPitchOutcome', 'ruleBasedOutcome', 'bookmakerSettlement', 'sources'])
            if e['evidenceLevel'] not in {'pending', 'documented', 'verified', 'disputed'}: raise ValueError('invalid evidenceLevel')
            for key in ['onPitchOutcome', 'ruleBasedOutcome', 'bookmakerSettlement']:
                if e[key] not in OUTCOMES: raise ValueError(f'invalid {key}')
            if not isinstance(e['sources'], list) or not all(source_reference(source) for source in e['sources']):
                raise ValueError('sources must be a list of nonblank references')
            if e['evidenceLevel'] in {'documented', 'verified'} and not e['sources']: raise ValueError('documented or verified outcome requires sources')
            if e.get('supersedesId') is not None: identifier(e['supersedesId'], 'supersedesId')
            receipt = e.get('receiptEvidence')
            if (receipt is not None or e['bookmakerSettlement'] != 'unknown') and not nonblank_text(receipt):
                raise ValueError('bookmaker settlement requires receiptEvidence as a nonblank note')
    else:
        require(e, ['decisionIds', 'note'])
        if not isinstance(e['decisionIds'], list): raise ValueError('decisionIds must be a list')
        for item in e['decisionIds']: identifier(item, 'decisionId')


def load(data):
    events = {}
    folder = data / 'events'
    if not folder.is_dir(): raise ValueError(f'journal not initialized: {folder}')
    for path in sorted(folder.glob('*.json')):
        try:
            with path.open(encoding='utf-8') as f: event = json.load(f, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('non-finite number')))
            check_event(event)
            if path.stem != event['id']: raise ValueError('filename does not match id')
            if event['id'] in events: raise ValueError('duplicate id')
            events[event['id']] = event
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            raise ValueError(f'{path}: {exc}') from exc
    check_links(events)
    return events


def check_links(events):
    sources = {}
    for e in events.values():
        if e['type'] == 'decision':
            identity = e['source']['identity']
            if identity in sources: raise ValueError(f'duplicate source identity: {identity}')
            sources[identity] = e['id']
        refs = [e['decisionId']] if e['type'] in {'status_revision', 'outcome'} else e.get('decisionIds', []) if e['type'] in {'review', 'method_change'} else []
        for ref in refs:
            if ref not in events or events[ref]['type'] != 'decision': raise ValueError(f'{e["id"]}: missing decision {ref}')
        if e['type'] == 'status_revision':
            decision = events[e['decisionId']]
            effective = timestamp(e['effectiveAt'], 'effectiveAt')
            original = timestamp(decision['originalTime']['value'], 'originalTime.value', True)
            kickoff = timestamp(decision['kickoff'], 'kickoff', True)
            if decision['cohort'] == 'prospective' and timestamp(e['appendedAt'], 'appendedAt') < timestamp(decision['appendedAt'], 'appendedAt'): raise ValueError(f'{e["id"]}: revision capture precedes parent capture')
            if original and effective < original: raise ValueError(f'{e["id"]}: revision precedes original decision')
            if effective > timestamp(e['recordedAt'], 'recordedAt'): raise ValueError(f'{e["id"]}: revision effective after recording')
            if e['status'] == 'selected':
                if not kickoff or effective >= kickoff or timestamp(e['recordedAt'], 'recordedAt') >= kickoff or timestamp(e['appendedAt'], 'appendedAt') >= kickoff: raise ValueError(f'{e["id"]}: cannot select at or after kickoff or with unknown kickoff')
                if decision['cohort'] == 'prospective':
                    if timestamp(e['recordedAt'], 'recordedAt') >= kickoff or not (e.get('preKickoffEvidence') == 'verified' and e.get('conditions') == 'met' and e.get('odds') is not None and isinstance(e['odds'], (int, float)) and not isinstance(e['odds'], bool) and e['odds'] > 1 and decision['market']['resolved']):
                        raise ValueError(f'{e["id"]}: prospective selection revision needs verified pre-kickoff capture, price and met conditions')
        if e['type'] == 'outcome':
            decision = events[e['decisionId']]
            recorded = timestamp(e['recordedAt'], 'recordedAt')
            kickoff = timestamp(decision['kickoff'], 'kickoff', True)
            if recorded < timestamp(decision['appendedAt'], 'appendedAt'): raise ValueError(f'{e["id"]}: outcome recorded before parent capture')
            if e['onPitchOutcome'] in {'won', 'lost', 'push', 'void', 'half-won', 'half-lost'}:
                if kickoff and recorded < kickoff:
                    raise ValueError(f'{e["id"]}: resolved outcome requires recording at or after kickoff')
                if not kickoff and (decision['cohort'] != 'historical-import' or e['evidenceLevel'] not in {'documented', 'verified'}):
                    raise ValueError(f'{e["id"]}: resolved outcome without kickoff requires a documented or verified historical result')
        if e['type'] == 'outcome' and e.get('supersedesId'):
            old = events.get(e['supersedesId'])
            if not old or old['type'] != 'outcome' or old['decisionId'] != e['decisionId'] or timestamp(old['recordedAt'], 'recordedAt') >= timestamp(e['recordedAt'], 'recordedAt'):
                raise ValueError(f'{e["id"]}: invalid supersedesId')


def add(data, path, now=None):
    # Serialize validation and publication among cooperating writers.
    with (data / '.write.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return add_locked(data, path, now)


def add_locked(data, path, now=None):
    with open(path, encoding='utf-8') as f: event = json.load(f, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('non-finite number')))
    if not isinstance(event, dict): raise ValueError('event must be an object')
    identifier(event.get('id'), 'id')
    events = load(data)
    existing = events.get(event['id'])
    if existing is not None:
        supplied = dict(event)
        if 'appendedAt' not in supplied: supplied['appendedAt'] = existing['appendedAt']
        if existing == supplied: return 'unchanged'
        raise ValueError('id already exists with different content')
    if 'appendedAt' in event: raise ValueError('appendedAt is assigned by the journal')
    clock = now or dt.datetime.now(dt.timezone.utc)
    if clock.tzinfo is None: raise ValueError('clock must have timezone')
    event['appendedAt'] = clock.astimezone(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    check_event(event)
    events[event['id']] = event
    check_links(events)
    folder = data / 'events'
    target = folder / (event['id'] + '.json')
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='.event-', suffix='.tmp', dir=folder, delete=False) as f:
            temp_name = f.name
            json.dump(event, f, indent=2, ensure_ascii=False, allow_nan=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        # Hard-link is atomic and fails if the final path already exists.
        os.link(temp_name, target)
    except FileExistsError:
        raise ValueError('event already exists; reload and retry') from None
    finally:
        if temp_name is not None:
            os.unlink(temp_name)
    return 'added'


def summary(events):
    result = {}
    for cohort in ('prospective', 'historical-import', 'demo'):
        decisions = [e for e in events.values() if e['type'] == 'decision' and e['cohort'] == cohort]
        counts, outcomes = Counter(), Counter()
        directions = {}
        for d in decisions:
            revisions = [e for e in events.values() if e['type'] == 'status_revision' and e['decisionId'] == d['id']]
            cutoff = timestamp(d['kickoff'], 'kickoff', True)
            valid = [e for e in revisions if cutoff and timestamp(e['effectiveAt'], 'effectiveAt') < cutoff and timestamp(e['recordedAt'], 'recordedAt') < cutoff and timestamp(e['appendedAt'], 'appendedAt') < cutoff]
            latest = max(valid, key=lambda e: (timestamp(e['effectiveAt'], 'effectiveAt'), timestamp(e['recordedAt'], 'recordedAt'), e['id']), default=None)
            status = latest['status'] if latest else d['status']
            counts[status] += 1
            records = [e for e in events.values() if e['type'] == 'outcome' and e['decisionId'] == d['id']]
            superseded = {e.get('supersedesId') for e in records}
            current = [e for e in records if e['id'] not in superseded]
            # Equivalent documented heads agree; disputed or conflicting heads need review.
            resolved = {e['onPitchOutcome'] for e in current if e['evidenceLevel'] in {'documented', 'verified'}}
            if any(e['evidenceLevel'] == 'disputed' for e in current) or len(resolved) > 1:
                outcome = 'needs-review'
            elif resolved:
                outcome = next(iter(resolved))
            else:
                outcome = 'pending'
            by_original = directions.setdefault(d['category'], {}).setdefault(d['status'], {})
            by_effective = by_original.setdefault(status, Counter())
            by_effective[outcome] += 1
            if status == 'selected':
                outcomes[outcome] += 1
        won, lost = outcomes['won'], outcomes['lost']
        result[cohort] = {'decisions': len(decisions), 'statuses': dict(sorted(counts.items())), 'selectedOnPitchOutcomes': dict(sorted(outcomes.items())), 'binaryHitRate': won / (won + lost) if won + lost else None, 'binaryResolved': won + lost, 'selectedTotal': counts['selected'], 'directionalOnPitchOutcomes': directions}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir', type=Path, default=ROOT, help='data directory')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init'); a = sub.add_parser('add'); a.add_argument('file', type=Path)
    sub.add_parser('validate'); sub.add_parser('summary')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            (args.dir / 'events').mkdir(parents=True, exist_ok=True); print('initialized')
        elif args.command == 'add': print(add(args.dir, args.file))
        elif args.command == 'validate': print(f'valid: {len(load(args.dir))} events')
        else: print(json.dumps(summary(load(args.dir)), indent=2, allow_nan=False))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'error: {exc}', file=sys.stderr); return 1
    return 0

if __name__ == '__main__': sys.exit(main())
