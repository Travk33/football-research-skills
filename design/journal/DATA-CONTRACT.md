# JSON storage and result contract

This is the implementation contract, not an already running database. Implement its rules with schema validation and small deterministic checks. JSON suits a personal, read-mostly archive with a modest number of entries. Reconsider SQLite or a service only if concurrent editing, large event datasets or authenticated browser editing becomes necessary.

## Repository layout for the future application

```text
journal/
  index.html
  styles.css
  app.js
  data/
    index.json                         # Derived manifest, not the source of truth
    slates/YYYY-MM-DD/<slate-id>-v1.json
    slates/YYYY-MM-DD/<slate-id>-v2.json
    verifications/<verification-id>.json
    reviews/<review-id>.json
  schemas/
    slate.schema.json
    verification.schema.json
    review.schema.json
  scripts/                             # Validate, regenerate index; no client secrets
```

Paths must work both at a domain root and under a repository subpath. Serve through HTTP for local testing rather than opening index.html through file://; local fetch restrictions can otherwise break JSON loading. [MDN local server guidance](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Tools_and_setup/set_up_a_local_testing_server).

The agent writes canonical files, validates, regenerates the manifest and commits. The static page reads only. No GitHub token, sports-feed key, raw private chat or account receipt belongs in the client bundle or public data. Never put the canonical records exclusively in localStorage.

## Core entities

Every canonical object has a stable `id`, integer `schemaVersion: 1`, and an exact UTC `recordedAt` timestamp. Unknown historical dates are null with a precision/reason field; do not invent midnight to create apparent precision. Display timezone is Europe/London, converted with daylight-saving rules. Preserve market/fixture provider IDs alongside readable names to avoid matching the wrong women's, youth, reserve or reverse fixture.

| Entity | Required content |
|---|---|
| Slate snapshot | id, revision, previousRevisionId or null, matchDate, timezone, category, cohort, recordedAt, researchTime, provenance, skillVersion, modelRun, fixtures, selections, builders, sources |
| Fixture | stable id, home/away display names and optional provider IDs, competition/season, scheduled kickoff, actual venue when known; kickoff null only for flagged historical gaps |
| Selection | stable id, fixtureId, exact market contract, decision, priceObservations, forecast or null, evidence, conditions, strongestCounterargument, sourceIds |
| Builder | stable id, fixtureId, two/three selection IDs, decision, actual joint price observation or null, dependence explanation, conditions, sourceIds |
| Verification | id, target snapshot/selection or builder IDs, evidence level, observed facts, onPitchOutcome, promotion assessment, ruleBasedOutcome, bookmakerSettlement, sources, supersedesId or null |
| Review | id, linked records, factual observation, alternative explanation, proposed method change, approval status, version affected, future evaluation plan |

`category` is exactly `wins-btts`, `other-markets` or `bet-builders`. `cohort` is `prospective`, `historical-import` or `demo`. Demo data must never enter published performance totals. Categories can have several slates on the same date. One logical selection retains its ID across revisions; a changed market line, player or side is a new selection linked with `replacesSelectionId`.

`researchTime` records the original claimed time, precision (`exact`, `approximate`, `date-only`, `unknown`) and evidence. `recordedAt` is the actual import/save time. A historical report may describe pre-match research without proving it was archived before kickoff. Keep `preKickoffEvidence` as `verified`, `claimed` or `unknown`, with supporting source. Do not backdate Git commits or assign today's skill/model version to last week's research. Unknown original versions stay null.

`provenance` identifies a sanitized report label, source kind and import limitations. Private machine paths, chat IDs and personal metadata stay outside public records. A hash may link to a locally retained source, but a hash generated today is not proof of publication before a historical kickoff.

## Original decisions and changes

Store `decision.status` as `candidate`, `conditional`, `watch`, `reserve`, `pass` or `selected`. Preserve `decision.originalLabel` and `decision.reason` rather than forcing old wording into a stronger claim. Only use selected when the record explicitly establishes an actionable research selection with its conditions satisfied; candidate does not mean placed or positive expected value.

Store `userDisposition` separately: `included`, `omitted` or `unknown`, with an evidence note and timestamp/precision. Included means explicitly chosen for a shortlist; it does not prove a bet was placed. Do not store wager amounts in this public journal.

Append a new snapshot for a lineup/price decision change, linking the preceding revision. The UI can show the latest pre-match revision, but must offer the original. After kickoff, corrections can repair transcription/provenance through an explicitly labeled amendment; they cannot enter the pre-match forecast cohort. A late missing-lineup check cannot retroactively satisfy a conditional pick.

Use an import identity based on source identity, slate, fixture, contract and source revision. Reimporting the same source is a no-op; a new source revision creates a linked snapshot. Serialize canonical writes. On a changed Git base, reload and compare IDs before writing; do not silently overwrite a concurrent update.

## Exact market and price fields

The market contract contains `family`, `subject`, `statistic`, `operator`, `line`, `period`, `settlementType`, `providerDefinition`, `rulesSourceId` and `rawLabel`. Null line is allowed where no threshold exists (e.g. match winner). Store selected team/player IDs, not only “home” or “Yes”. Preserve raw bookmaker wording as evidence. If a threshold can mean multiple things, mark contract unresolved and require review.

Examples of distinctions the schema/evaluator must preserve:

- Under 4 Asian total: four is a push. Under 4 in a three-way market: equality is a separate outcome; the under selection loses.
- Over 5 team corners, three-way: six or more is needed, exactly five loses.
- Player 1+ shots on target: count the named provider's SOT definition, not all shots or an unrelated feed.
- Fouls committed, fouls suffered and tackles are different statistics. Player start/substitution, non-participation and replacement rules require the exact contract.
- Regulation time plus stoppage time differs from extra time, half-time and qualification markets.

Each price observation includes decimal price, optional exact fractional numerator/denominator, bookmaker/source, region, observedAt with precision, source URL/ID, and `kind` (`direct`, `comparison`, `user-reported`). Preserve all observations; do not replace the pre-match price with the closing or winning price. Round for display only.

`forecast` is null unless a numerical forecast was actually made. Otherwise store probability, interval if available, method, sample, assumption notes and forecast time. Derive ordinary binary no-push break-even as `1 / decimalOdds`; label it a price hurdle, never our probability. For push/half-win/half-loss contracts, that simple unconditional success threshold is inadequate; hide it or use an explicitly modeled settlement distribution. A margin-adjusted market reference is a separate field, not a forecast.

Builders require the actual combined offered price to claim a priced recommendation. Individual leg prices may be retained, but their product is not the builder quote or a joint probability. Cross-match multiples, if added later, are explicit separate records; never infer an accumulator from all rows in a slate. Do not count a builder and its legs as three independent headline predictions.

## Evidence and outcomes

Evidence facts include metric, value/unit, named subject, fixture/sample IDs, count, competition, venue, timeframe, provider, source IDs and caveats. Facts and interpretations have distinct fields. Missing is null, not zero. Keep xG providers separate; keep player club/international samples separate. Store concise extracted facts and links, not whole scraped articles.

Verification `evidenceLevel`: `pending`, `documented`, `verified` or `disputed`. Documented means a saved report records the result; verified means the verification run checked suitable match/stat/rule evidence and retained its sources. A search title or model assertion alone is insufficient for a disputed player count.

`onPitchOutcome`: `won`, `lost`, `push`, `void`, `half-won`, `half-lost`, `pending`, `unknown`, `needs-review`. It refers to the ordinary market under its specified period/rules. Record fixture state separately (`scheduled`, `live`, `finished`, `postponed`, `abandoned`, `cancelled`). Postponement is not automatically a loss or a void.

`ruleBasedOutcome` records the assessed outcome after the documented eligible rules/promotions. `bookmakerSettlement` stays `unknown` unless a suitable actual receipt was supplied; if private evidence exists, publish at most a sanitized status under the user's publication scope. A correct directional prediction is not evidence of actual payment.

Two-goal promotion assessment has:

- `eligibility`: confirmed / not-eligible / unknown, with bookmaker, region, market, rule date/source and eligibility evidence.
- `trigger`: occurred / not-occurred / unknown, with selected team, validated score timeline, maximum lead and trigger time where known.
- `application`: applied / not-applied / needs-review, with reason; do not equate trigger with account eligibility.

For supported eligible result legs, a validated two-goal lead can mark that leg won under the promotion even if its ordinary outcome is lost/drawn. Other builder legs still need their own outcomes. A full-time 3–2 score alone cannot establish whether the winner led by two at any point. Reversed/disallowed goals do not count. Store both ordinary and promotion-aware outcomes without double-counting the entry. Refresh terms for the actual date/region; never apply a permanent global “2-up wins” switch. [bet365 UK offer reference](https://www.bet365.com/promos/en-gb/home/early-payout-offer).

Player-stat corrections create a superseding verification, retaining the previous result and explanation. A builder containing void/repriced legs needs confirmed builder rules and price before any return computation. Unsupported Asian quarter lines, abandonment rules or ambiguous substitution offers go to needs-review rather than an improvised evaluator.

## Metrics and counting

The initial archive's 20 research entries are 19 main-table directions plus one explicit watch, not all 116 games screened over those days. Six documented outcome records are not six verified bets. Builders count once in the top-level research-entry count; their component count is separate.

The default prospective performance cohort requires an explicitly selected, timestamped pre-kickoff decision and an exact contract. Declare the scoring policy before results: use the final valid revision saved strictly before a fixed cutoff, initially the scheduled kickoff recorded at creation, or actual kickoff if earlier. A delay does not retrospectively extend the cutoff; a formally postponed/rebooked fixture receives a linked new snapshot and an explicit new cutoff before resumption. If actual kickoff timing is uncertain, keep the timing gate unresolved. Never choose whichever revision won.

Score each logical entry once from that cutoff snapshot. A pre-cutoff downgrade/removal excludes it from the selected cohort; retain it in a visible withdrawn/watch/pass count. A changed contract retires the replaced selection from the active cohort while preserving its counterfactual record. A post-cutoff update cannot change cohort membership. Store the chosen snapshot ID with the evaluation so a later refresh cannot silently change historical totals.

Show all cohort entries, including unresolved ones, then calculate a resolved binary hit rate as won/(won + lost) with its denominator. Show pushes, voids, halves, pending and disputed separately; omit half outcomes from that simple binary rate rather than converting them into whole wins. Display resolution coverage so unresolved records cannot quietly improve the rate. Historical imports and passes/reserves are separate counterfactual views, never mixed into selected performance.

Keep ordinary, promotion-aware and actual-settlement metrics separate. Do not select whichever outcome makes the record look better. Correlated picks and repeated fixture revisions are not independent observations. Skill-version comparisons need comparable competitions/markets and sample-size caveats.

No ROI or bankroll chart in v1. Future hypothetical returns require a declared fixed-stake policy, full cohort, exact prices and rule-aware returns. Actual profit requires actual betting records, which this public design does not collect. Calibration requires recorded numeric forecasts; without them display “No forecast recorded”, not a curve made from odds.

## Minimum validation

Reject duplicate IDs, broken references, non-finite numbers, negative counts, probabilities outside [0,1], prices <=1 and invalid dates. Validate units: signed differences can be negative, counts cannot; never demand zero for missing values. Reject selected prospective records without verified pre-kickoff timing, price, resolved market and met conditions. Reject builders spanning fixtures or containing duplicate legs. Preserve null forecasts. Validate that source-linked facts resolve, amendments have chronology, and no private paths/secrets appear in public files.

Index counts derive from canonical records with one active revision per logical entry. A corrupt file produces a visible load warning and nonfinal summary, not a silent empty dataset. All computation is deterministic and testable without a model.
