"""Measure reported usage and score captured forecasts on ordinary outcomes."""

from collections import Counter, defaultdict
from collections.abc import Mapping
from datetime import date, datetime, timezone
import hashlib
import json
import math
import random
from statistics import mean

from .protocol import STATUSES, timestamp, validate_protocol


USAGE_FIELDS = {
    'inputTokens': 'input_tokens',
    'cachedInputTokens': 'cached_input_tokens',
    'outputTokens': 'output_tokens',
}
RATE_FIELDS = ('inputPerMillion', 'cachedInputPerMillion', 'outputPerMillion')
LOG_EPSILON = 1e-15
MIN_UNCERTAINTY_CLUSTERS = 20
BOOTSTRAP_REPLICATES = 2000
ORDINARY_OUTCOMES = frozenset({'won', 'lost', 'push', 'void', 'half-won', 'half-lost', 'pending', 'unknown', 'needs-review'})


def _hash(value):
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _count(value):
    return value if type(value) is int and value >= 0 else None


def _tokens(call):
    usage = call.get('usage')
    if not isinstance(usage, dict):
        usage = {}
    result = {name: _count(usage.get(key, usage.get(name))) for name, key in USAGE_FIELDS.items()}
    cached, total = result['cachedInputTokens'], result['inputTokens']
    if cached is not None and total is not None and cached > total:
        result['cachedInputTokens'] = None
    return result


def _rate_table(rates):
    if not isinstance(rates, dict) or not isinstance(rates.get('currency'), str) or not rates['currency'].strip():
        raise ValueError('rate table requires a currency')
    entries = rates.get('rates')
    if not isinstance(entries, list) or not entries:
        raise ValueError('rate table requires a nonempty rates array')
    parsed = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('model'), str) or not entry['model'].strip():
            raise ValueError('each rate requires a model')
        model = entry['model']
        try:
            start = date.fromisoformat(entry['effectiveFrom'])
            end = date.fromisoformat(entry['effectiveTo']) if entry.get('effectiveTo') is not None else None
        except (KeyError, ValueError, TypeError):
            raise ValueError(f'{model}: expected effectiveFrom and optional effectiveTo dates') from None
        values = tuple(entry.get(field) for field in RATE_FIELDS)
        if start == end or (end and end < start) or any(not _number(value) or value < 0 for value in values):
            raise ValueError(f'{model}: invalid rate window or per-million price')
        if (model, start) in parsed:
            raise ValueError(f'{model}: duplicate rate start date')
        parsed[model, start] = (end, values)
    identity = [(model, start.isoformat(), end.isoformat() if end else None, values)
                for (model, start), (end, values) in sorted(parsed.items())]
    return parsed, _hash([rates['currency'], identity])


def _estimate_cost(calls, tokens, rates):
    table, table_hash = _rate_table(rates)
    expenses, reasons = [], set()
    for call, counts in zip(calls, tokens):
        if None in counts.values():
            reasons.add('incomplete-reported-token-usage')
            continue
        model, start_time = call.get('reportedModel'), timestamp(call.get('startedAt'))
        if not model or not start_time:
            reasons.add('missing-reported-model-or-call-time')
            continue
        usage_date = start_time.date()
        matches = [(start, values) for (name, start), (end, values) in table.items()
                   if model == name and start <= usage_date and (end is None or usage_date < end)]
        if not matches:
            reasons.add('no-dated-rate-for-reported-model')
            continue
        _, (input_price, cached_price, output_price) = max(matches)
        cached = counts['cachedInputTokens']
        amount = ((counts['inputTokens'] - cached) * input_price + cached * cached_price
                  + counts['outputTokens'] * output_price) / 1_000_000
        expenses.append(amount)
    if reasons:
        return None, sorted(reasons)
    return {'amount': math.fsum(expenses), 'currency': rates['currency'], 'rateTableHash': table_hash,
            'basis': 'reported-model-token-usage-at-supplied-api-rates'}, []


def _coverage(manifest):
    tasks = manifest.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        return None
    coverage = []
    for task in tasks:
        if not isinstance(task, dict):
            return None
        stage = task.get('stage') or task.get('phase')
        fixture_ids, directions = task.get('fixtureIds'), task.get('directions')
        if (not isinstance(stage, str) or not stage.strip() or not isinstance(fixture_ids, list)
                or not isinstance(directions, list) or any(not isinstance(item, str) or not item.strip() for item in fixture_ids + directions)
                or len(set(fixture_ids)) != len(fixture_ids)):
            return None
        assigned = set()
        for direction in directions:
            separator = '/' if '/' in direction else ':'
            parts = direction.split(separator)
            if len(parts) != 3 or any(not part for part in parts) or parts[0] not in fixture_ids:
                return None
            assigned.add(parts[0])
            coverage.append((stage, parts[0], '/'.join(parts[1:])))
        coverage.extend((stage, fixture_id, '') for fixture_id in fixture_ids if fixture_id not in assigned)
        if not fixture_ids and not directions:
            coverage.append((stage, '', ''))
    if len(coverage) != len(set(coverage)):
        return None
    return _hash(sorted(coverage))


def _comparison_identity(manifest, calls):
    scope, categories = manifest.get('scope'), manifest.get('categories')
    return {
        'runId': manifest.get('runId'),
        'scopeHash': _hash([scope, sorted(categories)]) if isinstance(scope, dict) and isinstance(categories, list) else None,
        'evidenceHash': manifest.get('evidenceHash'),
        'workloadHash': _coverage(manifest),
        'workComplete': manifest.get('mode') == 'execute' and manifest.get('status') in {'complete', 'completed'},
    }


def usage_report(manifest, rates=None):
    """Return actual reported counts and optional estimates using dated API rates."""
    calls = manifest.get('calls') or []
    tokens = [_tokens(call) for call in calls]
    reported_calls = {key: sum(item[key] is not None for item in tokens) for key in USAGE_FIELDS}
    totals = {key: sum(item[key] for item in tokens) if calls and reported_calls[key] == len(calls) else None
              for key in USAGE_FIELDS}
    telemetry = manifest.get('sourceTelemetry') or manifest.get('evidenceTelemetry') or {}
    estimate, reasons = None, []
    if not calls:
        reasons.append('no-executed-model-calls')
    elif rates is None:
        reasons.append('no-api-rate-table-supplied')
    else:
        estimate, reasons = _estimate_cost(calls, tokens, rates)
    return {
        'schemaVersion': 1,
        'kind': 'usage-report',
        'requestId': manifest.get('requestId'),
        'modelCalls': len(calls),
        'requestedModels': dict(Counter(call['requestedModel'] for call in calls if call.get('requestedModel'))),
        'reportedModels': dict(Counter(call['reportedModel'] for call in calls if call.get('reportedModel'))),
        'usage': totals,
        'callsReportingTokens': reported_calls,
        'sourceRequests': _count(telemetry.get('networkRequests', telemetry.get('requests'))),
        'sourceCacheHits': _count(telemetry.get('cacheHits')),
        'estimatedApiCost': estimate,
        'subscriptionCost': None,
        'apiEstimateUnavailableReasons': reasons,
        'comparison': _comparison_identity(manifest, calls),
    }


def _reduction(baseline, candidate):
    if baseline is None or candidate is None:
        return None
    return {'baseline': baseline, 'candidate': candidate, 'difference': baseline - candidate,
            'percent': 100 * (baseline - candidate) / baseline if baseline else None}


def compare_costs(baseline, candidate):
    """Compare measured runs after verifying shared scope, evidence and work coverage."""
    reports = [value if value.get('kind') == 'usage-report' else usage_report(value)
               for value in (baseline, candidate)]
    first, second = (report['comparison'] for report in reports)
    reasons = []
    if not first['workComplete'] or not second['workComplete']:
        reasons.append('both-runs-must-complete-executed-work')
    for field in ('scopeHash', 'evidenceHash', 'workloadHash'):
        if not first.get(field) or first[field] != second.get(field):
            reasons.append(f'missing-or-different-{field}')
    run_ids = [item.get('runId') for item in (first, second)]
    if not all(isinstance(item, str) and item.strip() for item in run_ids):
        reasons.append('distinct-executed-runs-unverified')
    elif run_ids[0] == run_ids[1]:
        reasons.append('same-run-measurement')
    estimates = [report['estimatedApiCost'] for report in reports]
    compatible = not reasons
    estimate_delta = None
    if compatible:
        if not all(estimates):
            reasons.append('both-runs-need-complete-usage-and-dated-api-estimates')
        elif any(estimates[0][field] != estimates[1][field] for field in ('currency', 'rateTableHash')):
            reasons.append('runs-need-the-same-api-rate-table-and-currency')
        else:
            estimate_delta = _reduction(estimates[0]['amount'], estimates[1]['amount'])
            estimate_delta['currency'] = estimates[0]['currency']
            if estimates[0]['amount'] == 0:
                reasons.append('zero-baseline-api-estimate')
    return {
        'schemaVersion': 1,
        'kind': 'cost-comparison',
        'workComparable': compatible,
        'estimatedApiCostReduction': estimate_delta,
        'subscriptionCostReduction': None,
        'modelCallReduction': _reduction(*(report['modelCalls'] for report in reports)) if compatible else None,
        'sourceRequestReduction': _reduction(*(report['sourceRequests'] for report in reports)) if compatible else None,
        'reasons': reasons,
    }


def _pre_kickoff_status(decision, revisions, kickoff, now):
    original, captured = timestamp(decision.get('originalTime', {}).get('value')), timestamp(decision.get('appendedAt'))
    eligible = []
    for revision in revisions:
        effective, recorded, appended = (timestamp(revision.get(field))
                                         for field in ('effectiveAt', 'recordedAt', 'appendedAt'))
        if not all((effective, recorded, appended, kickoff, captured)):
            continue
        if not (effective <= recorded <= appended < kickoff and captured <= appended <= now):
            continue
        if original and effective < original:
            continue
        if revision['status'] == 'selected' and not _verified_selection(revision, decision):
            continue
        eligible.append((effective, recorded, appended, revision['id'], revision['status']))
    return max(eligible)[-1] if eligible else decision['status']


def _verified_selection(event, decision):
    evidence = event.get('preKickoffEvidence', event.get('originalTime', {}).get('preKickoffEvidence'))
    odds = event.get('odds')
    return (evidence == 'verified' and event.get('conditions') == 'met'
            and decision.get('market', {}).get('resolved') is True and _number(odds) and odds > 1)


def _source_ref(source):
    if isinstance(source, dict):
        return any(_source_ref(source.get(key)) for key in ('url', 'path', 'reference'))
    return isinstance(source, str) and bool(source.strip())


def _ordinary_outcome(records, kickoff, outcome_as_of):
    eligible = []
    after_cutoff = 0
    for record in records:
        appended, recorded = (timestamp(record.get(field)) for field in ('appendedAt', 'recordedAt'))
        if not (appended and recorded and kickoff and kickoff <= recorded <= appended):
            continue
        if appended > outcome_as_of:
            after_cutoff += 1
            continue
        eligible.append(record)
    superseded = {event.get('supersedesId') for event in eligible}
    current = [event for event in eligible if event['id'] not in superseded]
    if any(event.get('evidenceLevel') == 'disputed' for event in current):
        return 'needs-review', after_cutoff
    documented = {event['onPitchOutcome'] for event in current
                  if event.get('evidenceLevel') in {'documented', 'verified'}
                  and event.get('onPitchOutcome') in ORDINARY_OUTCOMES
                  and any(_source_ref(source) for source in event.get('sources', []))}
    if len(documented) > 1:
        return 'needs-review', after_cutoff
    return next(iter(documented), 'pending'), after_cutoff


def _probability(forecast, odds=None):
    value = forecast.get('probability')
    if not _number(value) or not 0 <= value <= 1:
        return None, 'missing-genuine-probability'
    source = forecast.get('probabilitySource')
    if isinstance(source, dict):
        source = source.get('method') or source.get('type')
    label = source.lower().replace('_', '-').replace(' ', '-') if isinstance(source, str) else ''
    if any(term in label for term in ('implied', 'reciprocal', 'odds-derived', 'odds-based', 'de-vig', 'market-odds')):
        return None, 'odds-derived-probability'
    if not label and _number(odds) and odds > 1 and math.isclose(value, 1 / odds, rel_tol=0, abs_tol=1e-9):
        return None, 'undocumented-probability-equals-reciprocal-odds'
    return value, None


def _in_scope(decision, status, kickoff, protocol):
    if not protocol:
        return True
    scope = protocol['scope']
    if not kickoff or not timestamp(protocol['startsAt']) <= kickoff < timestamp(protocol['endsAt']):
        return False
    if decision['category'] not in scope['categories'] or status not in scope['statuses']:
        return False
    fixture = decision.get('fixture', {})
    return all(str(fixture.get(field, decision.get(field))) in scope[scope_key]
               for field, scope_key in (('competitionId', 'competitionIds'), ('id', 'fixtureIds'))
               if scope_key in scope)


def _forecast_gate(decision, kickoff, protocol, now):
    original = decision.get('originalTime', {})
    made, recorded, captured = (timestamp(value) for value in
                                (original.get('value'), decision.get('recordedAt'), decision.get('appendedAt')))
    if not all((made, recorded, captured, kickoff)) or not made <= recorded <= captured <= now or captured >= kickoff:
        return 'capture-before-kickoff-unverified'
    if original.get('precision') != 'exact' or original.get('preKickoffEvidence') != 'verified':
        return 'original-forecast-time-unverified'
    if protocol and made < timestamp(protocol['registeredAt']):
        return 'forecast-precedes-protocol-registration'
    if decision.get('market', {}).get('resolved') is not True:
        return 'unresolved-market-contract'
    if decision['status'] == 'selected' and not _verified_selection(decision, decision):
        return 'selection-gates-unverified'
    return None


def _baseline_gate(decision, kickoff, protocol):
    baseline = decision.get('baselineForecast')
    if not isinstance(baseline, dict) or not isinstance(baseline.get('id'), str) or not baseline['id'].strip():
        return None, None, 'missing-baseline-forecast'
    baseline_id = baseline['id']
    if protocol and baseline_id != protocol['baselineId']:
        return baseline_id, None, 'different-baseline-method'
    if baseline.get('settlement') != 'onPitchOutcome' or baseline.get('decisionId', decision['id']) != decision['id']:
        return baseline_id, None, 'baseline-market-or-settlement-mismatch'
    recorded, captured = timestamp(baseline.get('recordedAt')), timestamp(decision.get('appendedAt'))
    if not recorded or not captured or not recorded <= captured < kickoff:
        return baseline_id, None, 'baseline-capture-before-kickoff-unverified'
    if protocol and recorded < timestamp(protocol['registeredAt']):
        return baseline_id, None, 'baseline-precedes-protocol-registration'
    value, reason = _probability(baseline, baseline.get('odds', decision.get('odds')))
    return baseline_id, value, reason


def _fixture_cluster(decision, kickoff):
    fixture = decision.get('fixture', {})
    identity = [fixture.get('id')] if fixture.get('id') else [fixture.get('home'), fixture.get('away')]
    return _hash([kickoff.isoformat() if kickoff else None, identity])


def _score(probability, outcome):
    clipped = min(1 - LOG_EPSILON, max(LOG_EPSILON, probability))
    return {'brier': (probability - outcome) ** 2,
            'log-loss': -math.log(clipped) if outcome else -math.log1p(-clipped)}


def _scores(rows, field, calibration=False):
    if not rows:
        return {'sampleSize': 0, 'brier': None, 'logLoss': None, 'calibration': []} if calibration else {
            'sampleSize': 0, 'brier': None, 'logLoss': None}
    scores = [_score(row[field], row['target']) for row in rows]
    result = {'sampleSize': len(rows), 'brier': mean(item['brier'] for item in scores),
              'logLoss': mean(item['log-loss'] for item in scores)}
    if calibration:
        bins = [[] for _ in range(10)]
        for row in rows:
            bins[min(9, int(row[field] * 10))].append(row)
        result['calibration'] = [
            {'from': index / 10, 'to': (index + 1) / 10, 'sampleSize': len(items),
             'fixtureClusters': len({row['fixtureCluster'] for row in items}),
             'meanPrediction': mean(row[field] for row in items) if items else None,
             'observedFrequency': mean(row['target'] for row in items) if items else None}
            for index, items in enumerate(bins)
        ]
    return result


def _status_summary(rows):
    outcomes = Counter(row['onPitchOutcome'] for row in rows)
    binary = outcomes['won'] + outcomes['lost']
    forecasts = [row for row in rows if row['scored']]
    return {'decisions': len(rows), 'onPitchOutcomes': dict(outcomes), 'binaryResolved': binary,
            'binaryHitRate': outcomes['won'] / binary if binary else None,
            'forecastScores': _scores(forecasts, 'probability', calibration=True)}


def _uncertainty(groups):
    if len(groups) < MIN_UNCERTAINTY_CLUSTERS:
        return None
    rng, draws = random.Random(0), []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = rng.choices(groups, k=len(groups))
        draws.append(math.fsum(total for total, _ in sample) / sum(size for _, size in sample))
    draws.sort()
    return {'method': 'fixture-cluster-percentile-bootstrap', 'replicates': BOOTSTRAP_REPLICATES,
            'confidenceLevel': 0.95, 'lower': draws[int(0.025 * len(draws))],
            'upper': draws[int(0.975 * len(draws)) - 1]}


def _pair_comparison(rows):
    candidate = _scores(rows, 'probability', calibration=True)
    baseline = _scores(rows, 'baselineProbability', calibration=True)
    differences = {}
    for metric in ('brier', 'log-loss'):
        groups = defaultdict(list)
        for row in rows:
            proposed = _score(row['probability'], row['target'])[metric]
            reference = _score(row['baselineProbability'], row['target'])[metric]
            groups[row['fixtureCluster']].append(proposed - reference)
        intervals = [(math.fsum(values), len(values)) for values in groups.values()]
        count = sum(size for _, size in intervals)
        differences[metric] = {'candidateMinusBaseline': math.fsum(total for total, _ in intervals) / count if count else None,
                               'confidenceInterval': _uncertainty(intervals)}
    return {'sampleSize': len(rows), 'fixtureClusters': len({row['fixtureCluster'] for row in rows}),
            'candidate': candidate, 'baseline': baseline, 'differences': differences}


def _study_gate(protocol, pairs, rows, now):
    if protocol is None:
        return ['no-preregistered-protocol']
    reasons = []
    if now < timestamp(protocol['outcomeCutoff']):
        reasons.append('outcome-window-still-open')
    if pairs['sampleSize'] < protocol['minimumPaired']:
        reasons.append('paired-observation-minimum-unmet')
    if pairs['fixtureClusters'] < max(protocol['minimumFixtureClusters'], MIN_UNCERTAINTY_CLUSTERS):
        reasons.append('fixture-cluster-minimum-unmet')
    nonbinary = {'push', 'void', 'half-won', 'half-lost'}
    if any(row['inScope'] and (row['forecastGateReason'] or (row['onPitchOutcome'] not in nonbinary
           and (not row['scored'] or row['baselineGateReason']))) for row in rows):
        reasons.append('incomplete-forecast-pair-or-ordinary-outcome-coverage')
    interval = pairs['differences'][protocol['primaryMetric']]['confidenceInterval']
    if interval is None or interval['upper'] >= 0:
        reasons.append('primary-loss-improvement-uncertain')
    return reasons


def evaluate_journal(events, protocol=None):
    """Score prospective journal forecasts on documented, ordinary binary events."""
    now = datetime.now(timezone.utc)
    protocol = validate_protocol(protocol) if protocol is not None else None
    outcome_as_of = min(now, timestamp(protocol['outcomeCutoff'])) if protocol else now
    events = list(events.values() if isinstance(events, Mapping) else events)
    cohorts = Counter(event['cohort'] for event in events if event['type'] == 'decision')
    revisions, outcomes = defaultdict(list), defaultdict(list)
    for event in events:
        if event['type'] == 'status_revision':
            revisions[event['decisionId']].append(event)
        elif event['type'] == 'outcome':
            outcomes[event['decisionId']].append(event)
    rows = []
    for decision in sorted(events, key=lambda event: event['id']):
        if decision['type'] != 'decision' or decision['cohort'] != 'prospective':
            continue
        decision_id, kickoff = decision['id'], timestamp(decision.get('kickoff'))
        status = _pre_kickoff_status(decision, revisions[decision_id], kickoff, now)
        outcome, after_cutoff = _ordinary_outcome(outcomes[decision_id], kickoff, outcome_as_of)
        probability, probability_reason = _probability(decision, decision.get('odds'))
        forecast_reason = _forecast_gate(decision, kickoff, protocol, now) or probability_reason
        baseline_id, baseline_probability, baseline_reason = _baseline_gate(decision, kickoff, protocol) if not forecast_reason else (None, None, 'candidate-forecast-ineligible')
        target = {'won': 1, 'lost': 0}.get(outcome)
        in_scope = _in_scope(decision, status, kickoff, protocol)
        rows.append({'decisionId': decision_id, 'category': decision['category'],
                     'originalStatus': decision['status'], 'preKickoffStatus': status,
                     'fixtureCluster': _fixture_cluster(decision, kickoff), 'inScope': in_scope,
                     'onPitchOutcome': outcome, 'outcomeRecordsAfterCutoff': after_cutoff, 'target': target,
                     'probability': probability if not forecast_reason else None, 'forecastGateReason': forecast_reason,
                     'baselineId': baseline_id, 'baselineProbability': baseline_probability, 'baselineGateReason': baseline_reason,
                     'scored': in_scope and forecast_reason is None and target is not None})
    scoped = [row for row in rows if row['inScope']]
    scored = [row for row in scoped if row['scored']]
    ids = [protocol['baselineId']] if protocol else sorted({row['baselineId'] for row in scored if row['baselineId']})
    pairs = {baseline_id: _pair_comparison([row for row in scored if row['baselineId'] == baseline_id
                                          and row['baselineGateReason'] is None]) for baseline_id in ids}
    reasons = _study_gate(protocol, pairs[protocol['baselineId']] if protocol else None, rows, now)
    by_status = {status: _status_summary([row for row in scoped if row['preKickoffStatus'] == status])
                 for status in sorted(STATUSES)}
    return {'schemaVersion': 1, 'kind': 'forecast-evaluation', 'protocolId': protocol['id'] if protocol else None,
            'outcomeAsOf': outcome_as_of.isoformat(), 'outcomeField': 'onPitchOutcome',
            'logLossClipEpsilon': LOG_EPSILON, 'minimumUncertaintyFixtureClusters': MIN_UNCERTAINTY_CLUSTERS,
            'coverage': {'decisionCohorts': dict(cohorts), 'scopedProspectiveDecisions': len(scoped),
                         'scoredProspectiveForecasts': len(scored), 'unscoredProspectiveDecisions': len(scoped) - len(scored),
                         'forecastGateReasons': dict(Counter(row['forecastGateReason'] for row in scoped if row['forecastGateReason']))},
            'selected': by_status.pop('selected'), 'researchDirections': by_status,
            'pairedComparisons': pairs, 'observations': rows,
            'predictiveSuperiority': 'supported-in-recorded-protocol-cohort' if not reasons else 'unestablished',
            'superiorityGateReasons': reasons}
