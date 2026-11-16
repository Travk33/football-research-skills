#!/usr/bin/env python3
"""One-time, repeatable historical import. Never represents pre-match capture.

Sources are the preserved reports; journal.add supplies the real append time.
Rerunning identical input is a no-op. Changed source content fails closed.
"""
import datetime as dt
import hashlib
import json
import tempfile
from pathlib import Path

import journal

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'journal/data'
COUNTS = {'added': 0, 'unchanged': 0}


def read(path):
    return json.loads((ROOT / path).read_text())


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def save(event):
    old = DATA / 'events' / (event['id'] + '.json')
    event['schemaVersion'] = 1
    event['recordedAt'] = json.loads(old.read_text())['recordedAt'] if old.exists() else now()
    with tempfile.TemporaryDirectory(prefix='football-journal-import-') as directory:
        path = Path(directory) / 'event.json'
        path.write_text(json.dumps(event, ensure_ascii=False, indent=2) + '\n')
        result = journal.add(DATA, path)
    COUNTS[result] += 1


def decision(ident, date, home, away, label, status, report, *, odds=None,
             category='wins-btts', kickoff=None, original=None, resolved=True, **extra):
    event = dict(id=ident, type='decision', cohort='historical-import', matchDate=date,
                 category=category, fixture={'home': home, 'away': away},
                 market={'rawLabel': label, 'resolved': resolved, 'period': 'regulation time'},
                 status=status, source={'identity': report + '#' + ident, 'report': report,
                                       'sha256': hashlib.sha256((ROOT / report).read_bytes()).hexdigest()},
                 originalTime=original or {'value': None, 'precision': 'unknown', 'preKickoffEvidence': 'claimed'},
                 kickoff=kickoff, evidence={'report': report}, countercase={'report': report},
                 conditions='Not independently closed before kickoff in this import.', odds=odds,
                 probability=None, importNote='Retrospective import after the outcome. Not a prospective forecast.',
                 actualPlacementVerified=False, **extra)
    save(event)
    return ident


def outcome(ident, result, sources, *, evidence='documented', rules='unknown', **extra):
    save(dict(id=ident + '-result', type='outcome', decisionId=ident, evidenceLevel=evidence,
              onPitchOutcome=result, ruleBasedOutcome=rules, bookmakerSettlement='unknown',
              sources=sources, **extra))


def price(raw):
    if '/' in raw:
        a, b = raw.split('/')
        return 1 + float(a) / float(b)
    return float(raw)


def import_earlier():
    report = 'research/methodology-audit-2026-11-14/results.json'
    statuses = ['candidate', 'candidate', 'candidate', 'conditional', 'conditional', 'candidate', 'watch', 'watch',
                'conditional', 'conditional', 'conditional', 'conditional', 'conditional', 'conditional',
                'conditional', 'reserve', 'watch', 'reserve', 'reserve', 'pass']
    times = ['20:00', '20:00', '20:00', '20:00', '17:45', '17:45', '20:00', '20:00',
             '19:45', '15:00', '14:30', '20:00', '17:45', '15:00', '18:30', '14:00', '15:00', '20:30', '16:00', '19:00']
    grouped = {}
    for row, status, time in zip(read(report)['rows'], statuses, times):
        home, away = row['fixture'].split('–', 1)
        ident = 'import-' + row['date'] + '-' + row['id']
        decision(ident, row['date'], home, away, row['market_direction'], status, report,
                 odds=price(row['archived_reference_quote']), kickoff=row['date'] + 'T' + time + ':00Z',
                 originalStatus=row['archived_research_status_summary'], originalQuote=row['archived_reference_quote'],
                 includedInUserReportedWinningGroup=row['included_in_discussed_successful_group'],
                 statusNormalization='Retains row qualifiers; main direction is not evidence that lineup/price conditions closed.',
                 archiveAudit='research/methodology-audit-2026-11-14/audit.md')
        outcome(ident, 'won' if row['direction_occurred_at_full_time'] else 'lost', row['result_sources'] + [report],
                fullTimeScore=row['full_time_score_home_away'], verificationDate='2026-11-14',
                earlyPayoutNeededForDirection=row['early_payout_needed_for_direction'])
        grouped.setdefault(row['date'], []).append(ident)
    for date, ids in grouped.items():
        save(dict(id='import-' + date + '-review', type='review', decisionIds=ids, matchDate=date,
                  note='User-reported successful group archived with original candidate/watch/reserve/pass qualifiers. '
                       'All directions, including the failed Monaco watch and omitted Brighton win, remain visible. '
                       'No actual settlement or profit is established; no causal explanation of a three-group streak is identified.',
                  source='research/methodology-audit-2026-11-14/audit.md', retrospective=True))


def import_nov12():
    report = 'research/2026-11-12/archive/thursday-12-november-2026-results-audit.md'
    facts = read('research/2026-11-12/archived-match-facts.json')['matches']
    # slug, match, market, status, category, original price if preserved, original wording
    rows = [
        ('england-win', '5181858', 'England win', 'conditional', 'wins-btts', 1.25, 'Conditional leading candidate'),
        ('england-corners', '5181858', 'England 6+ team corners', 'reserve', 'other-markets', 1.50, 'Replacement alternative; not an extra standalone recommendation'),
        ('montenegro-win', '5181930', 'Montenegro win', 'conditional', 'wins-btts', 1.30, 'Conditional leading candidate'),
        ('albania-win', '5181902', 'Albania win', 'watch', 'wins-btts', None, 'Higher-risk watch; not core'),
        ('albania-dnb', '5181902', 'Albania draw no bet', 'reserve', 'other-markets', 1.364, 'Secondary; approximately 1.364'),
        ('armenia-cyprus-under35', '5181929', 'Armenia–Cyprus under 3.5 match goals', 'reserve', 'other-markets', 1.25, 'Secondary; separate from user ticket Under 4 contract'),
        ('italy-france-btts', '5181797', 'Italy–France BTTS Yes', 'pass', 'wins-btts', 1.571, 'Explicit price pass; approximate quoted decimal'),
        ('belarus-win', '5181903', 'Belarus win', 'reserve', 'wins-btts', None, 'Short-price reserve; not leading core'),
        ('drcongo-win', '6040263', 'DR Congo win', 'watch', 'wins-btts', None, 'Later fourfold assessment; limited pre-match evidence; not top-list pick'),
    ]
    ids = []
    for slug, match, label, status, category, odds, wording in rows:
        f = facts[match]
        ident = decision('import-2026-11-12-' + slug, '2026-11-12', f['home'], f['away'], label, status, report,
                         category=category, odds=odds, kickoff=f['kickoff'], originalStatus=wording)
        outcome(ident, 'won', [f['source'], report], fullTimeScore=f['score'],
                verificationDate='2026-11-12', observedEventCount=6 if slug == 'england-corners' else None)
        ids.append(ident)
    pairs = [
        ('turkiye-pair', '5181796', 'Arda Güler 1+ SOT + Zeki Çelik 2+ tackles', 'conditional', 'Supported lower-threshold pair', 'won',
         [{'player': 'Arda Güler', 'event': 'SOT', 'threshold': 1, 'count': 3, 'minutes': 90, 'started': True},
          {'player': 'Zeki Çelik', 'event': 'tackles', 'threshold': 2, 'count': 2, 'minutes': 20, 'started': False}]),
        ('england-pair', '5181858', 'Elliot Anderson 1+ foul + Luka Vušković 1+ foul', 'conditional', 'Supported lower-threshold pair', 'won',
         [{'player': 'Elliot Anderson', 'event': 'fouls', 'threshold': 1, 'count': 1, 'minutes': 90, 'started': True},
          {'player': 'Luka Vušković', 'event': 'fouls', 'threshold': 1, 'count': 1, 'minutes': 90, 'started': True}]),
        ('italy-pair', '5181797', 'Michael Olise 1+ SOT + Sandro Tonali 1+ foul', 'conditional', 'Provisional/short pair', 'won',
         [{'player': 'Michael Olise', 'event': 'SOT', 'threshold': 1, 'count': 1, 'minutes': 90, 'started': True},
          {'player': 'Sandro Tonali', 'event': 'fouls', 'threshold': 1, 'count': 1, 'minutes': 90, 'started': True}]),
        ('spain-pair', '5181857', 'Adam Hložek 1+ shot + Marc Cucurella 2+ tackles', 'watch', 'Watchlist only; Cucurella line/price unverified', 'lost',
         [{'player': 'Adam Hložek', 'event': 'shots', 'threshold': 1, 'count': 1, 'minutes': 85, 'started': True},
          {'player': 'Marc Cucurella', 'event': 'tackles', 'threshold': 2, 'count': 0, 'minutes': 90, 'started': True}]),
    ]
    for slug, match, label, status, wording, result, legs in pairs:
        f = facts[match]
        ident = decision('import-2026-11-12-' + slug, '2026-11-12', f['home'], f['away'], label, status, report,
                         category='bet-builders', kickoff=f['kickoff'], originalStatus=wording, resolved=False,
                         combinedQuoteStatus='No observed combined quote; singles were not multiplied.',
                         contractNote='Statistical event thresholds identified; exact operator contract not verified.')
        outcome(ident, result, [f['source'], report], rules='needs-review' if slug == 'turkiye-pair' else 'unknown',
                statisticalLegs=legs, verificationDate='2026-11-12',
                outcomeScope='Statistical thresholds only, not actual builder settlement. Selected non-starter may be void.')
        ids.append(ident)
    save(dict(id='import-2026-11-12-review', type='review', decisionIds=ids, matchDate='2026-11-12',
              note='Preserve successful ordinary directions and failed Cucurella watch pair without promoting watches/passes. '
                   'Cucurella had 0 tackles, one ground duel and limited opponent exposure. Çelik came off bench; '
                   'event counts do not determine pre-match non-starter settlement. User-reported tickets remain separate.',
              source=report, retrospective=True))


def import_nov13():
    report = 'research/2026-11-13/archive/friday-13-november-2026-expanded-review.md'
    result_report = 'research/2026-11-13/result-verification.json'
    rows = [
        ('scotland-btts-no', 'Scotland', 'North Macedonia', 'BTTS No', 'conditional', 'wins-btts', 1.533, 'lost', '5181784', '2–1', None),
        ('iceland-corners', 'Bulgaria', 'Iceland', 'Iceland 5+ team corners', 'conditional', 'other-markets', 1.80, 'lost', '5181957', '0–5', 1),
        ('netherlands-corners', 'Netherlands', 'Greece', 'Netherlands 6+ team corners', 'conditional', 'other-markets', 1.727, 'lost', '5181833', '7–0', 5),
        ('luxembourg-btts-no', 'Luxembourg', 'Estonia', 'BTTS No', 'conditional', 'wins-btts', 1.667, 'won', '5181958', '0–1', None),
        ('germany-win', 'Serbia', 'Germany', 'Germany win', 'conditional', 'wins-btts', 1.25, 'won', '5181834', '1–3', None),
        ('iceland-win', 'Bulgaria', 'Iceland', 'Iceland win', 'reserve', 'wins-btts', 1.70, 'won', '5181957', '0–5', None),
        ('netherlands-win', 'Netherlands', 'Greece', 'Netherlands win', 'reserve', 'wins-btts', 1.571, 'won', '5181833', '7–0', None),
    ]
    ids = []
    for slug, home, away, label, status, category, odds, result, match, score, count in rows:
        source = report if status != 'reserve' else 'research/2026-11-13/archive/friday-13-november-2026-market-choice-audit.md'
        ident = decision('import-2026-11-13-' + slug, '2026-11-13', home, away, label, status, source,
                         category=category, odds=odds, kickoff='2026-11-13T19:45:00Z',
                         originalStatus='Reserve alternative' if status == 'reserve' else 'Retained direction/candidate; lineup and price gates not documented closed',
                         excludedFromFutureSuggestions=label == 'BTTS No',
                         presentationIssue='Conditional directions were treated as main-ticket choices in discussion; retain this failure explicitly.')
        outcome(ident, result, ['https://www.fotmob.com/api/data/matchDetails?matchId=' + match, result_report],
                evidence='verified', fullTimeScore=score, observedEventCount=count,
                observedAt=read(result_report)['observed_at_utc'])
        ids.append(ident)
    save(dict(id='import-2026-11-13-review', type='review', decisionIds=ids, matchDate='2026-11-13',
              note='Three of five discussed main directions failed. Preserve conditional status but audit the communication failure. '
                   'Iceland and Netherlands won emphatically yet failed exact corner thresholds. Dominance is not a corner count. '
                   'Historical BTTS No remains recorded but is excluded from future suggested markets by user preference.',
              source='research/2026-11-13/archive/friday-13-november-2026-market-choice-audit.md', retrospective=True))


def import_nov14():
    report = 'research/2026-11-14/coverage-inventory.json'
    coverage = read(report)
    results = {r['id']: r for r in read('research/2026-11-14/post-match-results.json')['fixtures']}
    original = {'value': '2026-11-14T03:45:11+00:00', 'precision': 'exact', 'preKickoffEvidence': 'verified'}
    candidates = {r['fixture_id']: r for r in read('research/2026-11-14/decision-ledger.json')['research_candidates']}
    ids = []
    for fixture in coverage['fixtures']:
        fid = fixture['id']
        result = results[fid]
        a, b = [int(x) for x in result['score'].replace('–', '-').split('-')]
        sides = ['away'] if fid in {'2047895', '2047891'} else ['home', 'away'] if fid == '2047897' else ['home']
        sources = ['https://www.fotmob.com/api/data/matches?date=20261114', 'research/2026-11-14/post-match-results.json']
        if fid in {'2047892', '2047890'}:
            sources.append('https://www.fotmob.com/api/data/matchDetails?matchId=' + ('5181870' if fid == '2047892' else '5181846'))
        for side in sides:
            status = 'conditional' if fid == '2047892' else 'reserve' if fid == '2047890' else 'pass'
            quote = fixture['prices'][side]
            ident = decision('import-2026-11-14-' + fid + '-' + side + '-win', '2026-11-14', fixture['home'], fixture['away'],
                             fixture[side] + ' win', status, report, odds=quote['decimal'], kickoff=fixture['kickoff'], original=original,
                             originalStatus=candidates.get(fid, {}).get('status', fixture['decision_reason']),
                             decisionReason=fixture['decision_reason'], coverageLevel=fixture['coverage'],
                             priceObservation=fixture['prices'], missing=fixture['missing'],
                             originalDecisionLedger='research/2026-11-14/decision-ledger.json',
                             scopeNote='Screened direction, not a final selection. Conditional/reserve only where explicitly retained.')
            outcome(ident, 'won' if (a > b if side == 'home' else b > a) else 'lost', sources,
                    evidence='verified', fullTimeScore=result['score'],
                    observedAt=read('research/2026-11-14/post-match-results.json')['observed_at_utc'])
            ids.append(ident)
        btts_price = 11 / 7 if fid == '2047892' else None
        ident = decision('import-2026-11-14-' + fid + '-btts-yes', '2026-11-14', fixture['home'], fixture['away'],
                         'BTTS Yes', 'pass', report, odds=btts_price, kickoff=fixture['kickoff'], original=original,
                         originalStatus='Price pass' if fid == '2047892' else 'Not shortlisted / insufficient evidence; quote unverified',
                         decisionReason=fixture['decision_reason'], coverageLevel=fixture['coverage'],
                         priceObservation={'bookmaker': 'Paddy Power UK', 'fractional': '4/7', 'observedAt': '2026-11-14T03:38:42+00:00',
                                           'source': 'https://www.paddypower.com/football/uefa-nations-league-a/portugal-v-denmark-36192523?tab=goals'} if fid == '2047892' else None,
                         scopeNote='Screened BTTS Yes direction; not a final selection. Unobserved prices remain null.')
        outcome(ident, 'won' if a > 0 and b > 0 else 'lost', sources, evidence='verified', fullTimeScore=result['score'],
                observedAt=read('research/2026-11-14/post-match-results.json')['observed_at_utc'])
        ids.append(ident)
    save(dict(id='import-2026-11-14-review', type='review', decisionIds=ids, matchDate='2026-11-14', category='wins-btts',
              source='research/2026-11-14/post-match-review.md', coverageSource=report, finalSelectionCount=0,
              originalFinalSelectionCount=0, originalDecisionAt=original['value'], retrospective=True,
              note='Zero final selections in original ledger; Portugal conditional lost, Sweden reserve won. Candidate-quality review still required. '
                   'Later xG retrieval changes interpretation of prior matches and is explicitly post-match evidence. '
                   'Record every screened winner/BTTS direction including winning passes; no hindsight promotions or inferred actual wagers.'))


def import_nov13_supplement():
    report = 'research/2026-11-13/archive/friday-13-november-2026-expanded-review.md'
    day_report = 'research/2026-11-13/audit-evidence/day-results-check.json'
    day = read(day_report)
    facts = {r['match_id']: r for r in day['results']}
    # Important published reserves/passes, not the entire 22-fixture outside-UEFA screen.
    rows = [
        ('andorra-under25', '5181878', 'Andorra–Gibraltar under 2.5 goals', 'reserve', 'other-markets', 1.333, 'won', 'Low creation, small current sample'),
        ('switzerland-win', '5181785', 'Switzerland win', 'reserve', 'wins-btts', 1.667, 'lost', 'Reverse weak; Xhaka absent; draw clinches promotion'),
        ('slovakia-win', '5181942', 'Slovakia win', 'pass', 'wins-btts', 1.364, 'lost', 'Not promoted; absences and draw incentives'),
        ('slovakia-corners', '5181942', 'Slovakia 7+ team corners', 'reserve', 'other-markets', 2.00, 'won', 'Reserve; six absences affect possession and delivery'),
        ('moldova-btts', '5181941', 'Moldova–Kazakhstan BTTS Yes', 'reserve', 'wins-btts', 2.00, 'won', 'Reserve; Kazakhstan away chance quality and availability matter'),
        ('mali-win', '6040377', 'Mali win', 'reserve', 'wins-btts', 1.286, 'won', 'African reserve; draw tendency, Bissouma omission and demanding price'),
        ('mozambique-win', '6040400', 'Mozambique win', 'reserve', 'wins-btts', 1.50, 'lost', 'Reserve only; 4–1 prior score concealed 5–4 SOT'),
        ('saintlucia-win', '6375163', 'Saint Lucia win', 'pass', 'wins-btts', 1.20, 'won', 'Price pass; prior 5–2 conceded 20 shots and 11 SOT'),
        ('burkina-win', '6040278', 'Burkina Faso win', 'pass', 'wins-btts', 1.533, 'won', 'Pass; insufficient underlying attacking separation'),
    ]
    ids = []
    for slug, match, label, status, category, odds, result, wording in rows:
        f = facts[match]
        home, away = f['fixture'].split(' vs ', 1)
        ident = decision('import-2026-11-13-' + slug, '2026-11-13', home, away, label, status, report,
                         category=category, odds=odds, kickoff=f['kickoff_utc'], originalStatus=wording,
                         outcomeSourceScope='Important additional archived direction; not exhaustive outside-UEFA reconstruction.')
        sources = [day['day_feed_url'], day_report]
        extra = {}
        if slug == 'slovakia-corners':
            raw_path = 'research/2026-11-13/audit-evidence/fotmob-match-5181942.json'
            raw = read(raw_path)
            stat = next(s for g in raw['content']['stats']['Periods']['All']['stats'] for s in g['stats'] if s.get('key') == 'corners')
            assert stat['stats'] == [9, 5]
            provenance = read('research/2026-11-13/audit-evidence/slovakia-corners-verification.json')
            extra = {'observedEventCount': 9, 'opponentCorners': 5,
                     'statisticObservedAt': provenance['observedAt'],
                     'statisticTimeBasis': 'Timestamp of saved raw response; observedAt below refers to the separate day feed.'}
            sources += [raw_path, f['source_url']]
        outcome(ident, result, sources, evidence='verified', fullTimeScore=f['score'], observedAt=day['retrieved_at_utc'], **extra)
        ids.append(ident)
    props_report = 'research/2026-11-13/audit-evidence/nov13-player-prop-verification.json'
    props = read(props_report)
    for match in props['matches']:
        players = {p['player']: p for p in match['players']}
        if match['match_id'] == '5181834':
            w, k = players['Florian Wirtz'], players['Joshua Kimmich']
            items = [('germany-player-pair', 'Serbia', 'Germany', 'Florian Wirtz 3+ shots + Joshua Kimmich to be fouled 1+', None,
                      'Exploratory pair; no promoted builder or verified combined quote',
                      w['total_shots_regulation'] >= 3 and k['fouls_drawn'] >= 1,
                      [dict(w, selectedEvent='shots', selectedThreshold=3), dict(k, selectedEvent='fouls drawn', selectedThreshold=1)])]
        else:
            m = players['John McGinn']
            items = [('mcginn-' + str(line) + '-fouled', 'Scotland', 'North Macedonia', 'John McGinn to be fouled ' + str(line) + '+', odd,
                      'Separate player watch; no Scotland builder promoted' + ('; materially riskier alternative' if line == 3 else ''),
                      m['fouls_drawn'] >= line, [dict(m, selectedEvent='fouls drawn', selectedThreshold=line)])
                     for line, odd in [(2, 1.143), (3, 1.444)]]
        for slug, home, away, label, odds, wording, hit, legs in items:
            ident = decision('import-2026-11-13-' + slug, '2026-11-13', home, away, label, 'watch', report,
                             category='bet-builders', odds=odds, kickoff=match['date_utc'], originalStatus=wording, resolved=False,
                             quoteNote='Individual reference only where present; no observed combined quote.')
            outcome(ident, 'won' if hit else 'lost', [match['source_url'], props_report], evidence='verified',
                    fullTimeScore=match['score'], statisticalLegs=legs, observedAt=props['retrieved_at_utc'],
                    outcomeScope='Statistical thresholds only; no verified bookmaker settlement.', redCards=match['red_cards'])
            ids.append(ident)
    save(dict(id='import-2026-11-13-supplement-review', type='review', decisionIds=ids, matchDate='2026-11-13',
              source=report, retrospective=True, previousReviewId='import-2026-11-13-review',
              note='Additional important reserves/passes and exploratory player directions imported. Switzerland and Mozambique reserves lost; '
                   'other winning reserves/passes remain unpromoted. Wirtz had 5 shots and Kimmich drew 1 foul, but the Germany pair was exploratory '
                   'and Serbia had two dismissals. McGinn drew 1 foul and missed both separate watch lines. '
                   'This supplements, rather than rewrites, the earlier import; the full outside-UEFA screen remains in the source report.'))


def main():
    (DATA / 'events').mkdir(parents=True, exist_ok=True)
    import_earlier()
    import_nov12()
    import_nov13()
    import_nov14()
    import_nov13_supplement()
    save(dict(id='method-2026-11-15-journal-and-decision-quality', type='method_change', decisionIds=[],
              note='Mandatory journal workflow added to all three research skills. Bounded decisive-data retrieval, '
                   'favourable-XI substantive-case check, symmetric sensitivity checks and exact-market exposure review added. '
                   'No fitted feature weights or automatic domestic-league edge. Evaluate process adherence over the next four completed research slates.',
              source='journal/active-lessons.md', reviewSource='research/2026-11-14/post-match-review.md',
              approval='User requested journal and skill improvements; no UI or automation requested.',
              alternativeExplanation='Short samples, finishing, penalties and game state contribute to outcomes; not every loss proves a process error.'))
    events = journal.load(DATA)
    print(json.dumps({'writes': COUNTS, 'totalEvents': len(events),
                      'decisions': sum(e['type'] == 'decision' for e in events.values())}))


if __name__ == '__main__':
    main()
