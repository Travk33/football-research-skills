# Scoped research pipeline

The scope comes from the user's request: dates, competitions, teams, explicit fixtures and market categories. There is no fixed 44-game limit. Python 3.11+ and the installed authenticated Codex CLI are required for model execution; collection, planning and journal evaluation use the standard library without model calls.

## What is implemented

| Component | Behaviour |
|---|---|
| Collection | FotMob fixture discovery, both-team history, requested recent match-detail statistics, venue/gender checks when available, source times and explicit gaps |
| Shared cache | Resource-specific freshness, reuse across market categories, bounded requests; new retrievals do not change original source observation times |
| Screening | Separate winner/BTTS directions and compact other-market families; survivors and close exclusions receive deeper analysis |
| Routing | Explicit GPT-6 Luna/medium extraction where available, GPT-6.2 Astra/high lead and GPT-6.2 Sol/high independent review by default; configurable routes, no silent model fallback |
| Limits | Request, call, concurrency and timeout limits; configurable batching; incomplete work remains visibly incomplete |
| Final decisions | Exact quoted contract and required source/role checks; missing material inputs prevent final promotion |
| Journal | Execute runs archive original evidence, decisions, passes, failed-stage screens and zero-final slates through the existing writer |
| Measurement | Actual available token counts, model calls and cache telemetry; dated API-rate estimates when all required observations exist |
| Evaluation | Prospective forecast scoring and paired, pre-registered baseline comparisons; historical imports and odds-derived forecasts excluded |

**Limits:** this is a collection/screening and decision-support implementation. It does not automatically inspect a logged-in bookmaker, verify every news claim, calibrate a forecasting model, or establish an edge. Public-provider responses can be absent or change shape. The automated model stages analyse the supplied evidence only; the active research chat must retrieve material missing news, current prices, player ledgers and detailed tactical evidence through the relevant skill, then supply a new sourced bundle. Do not call a thin bundle a completed deep investigation.

## Normal use from a research chat

1. Translate the user's requested scope into a request; use `discover` for current provider IDs. Never silently broaden scope.
2. Collect shared data once. `historyDetails` controls how many recent rows per team receive advanced-stat retrieval; it does not define sufficient evidence for a selection. Initial default is three, with eight historical result rows. Broaden meaningful finalists to the requested 5–10 comparable detailed rows and a broader baseline as sources permit. Use a narrower follow-up request and the same cache to avoid re-fetching the entire slate.
3. Read the relevant skill and journal lessons. Resolve decisive gaps, including team news and actual markets. `enrich` appends sourced observations to a new evidence artifact; prior artifacts remain intact.
4. Plan the exact routes/call bounds, then execute within the research task's authorization. Read the resulting dossiers and challenges. The selected lead remains responsible for substantive judgment; structural validation cannot verify every tactical claim.
5. Refresh material XI, price and contract observations before final promotion. Changed evidence requires a new run directory, preserving earlier decisions. Review outcomes later with `$football-journal`.

## Commands

```sh
# List scheduled fixtures and competition/team/match IDs; no model calls.
python3 scripts/pipeline.py discover --date 2026-11-21 --out outputs/fixtures.json

# Example scope: English Premier League (provider ID 47), not a fixed fixture count.
python3 scripts/pipeline.py init --id saturday-example --date 2026-11-21 \
  --competition-id 47 --gender male --out outputs/request.json

# Cache location is shared across requests and categories.
python3 scripts/pipeline.py collect --request outputs/request.json --out outputs/evidence.json

# Plan writes tasks but makes no model calls.
python3 scripts/pipeline.py run --request outputs/request.json \
  --evidence outputs/evidence.json --output-dir outputs/run

# Execute explicit model routes; archives into this project's journal by default.
python3 scripts/pipeline.py run --request outputs/request.json \
  --evidence outputs/evidence.json --output-dir outputs/run --execute

python3 scripts/pipeline.py usage --manifest outputs/run/manifest.json --out outputs/usage.json
python3 scripts/pipeline.py evaluate --out outputs/evaluation.json
```

Replace the dates/scope with the actual request. Repeat `--date`, `--competition-id`, `--fixture-id` or `--team-id` for multiple values. Different filter families intersect; IDs within a family are OR. An unrestricted request requires `--all-competitions`. Builder requests use `--category bet-builders --builder-fixture-id ID`; the default maximum is five and is explicitly configurable in `limits.maxBuilderFixtures`.

An existing artifact with different contents is never overwritten. Use a fresh filename/run directory for a refresh. Identical completed runs are reused without charging model calls; after kickoff they are returned as historical, not current final selections. A failed run may resume successful tasks only with the same request and evidence. The call budget includes failed attempts. CLI failures return exit code 2 and retain their artifacts. Do not repeatedly retry a usage-limit error; disclose it or use a user-approved explicit route change in a new request.

The 6.2 defaults apply to newly generated requests or omitted routing fields. Existing requests that explicitly pin older models retain those routes; create a new request/run when migrating them. Check Luna availability in the execution surface: the CLI and chat subagent menu can differ. An unavailable Luna route remains a visible failure until an explicit alternative is chosen and recorded; there is no automatic costlier fallback.

## News, prices, rules and player data

The collector never invents these. In a supplement, identify the original bundle with `evidenceHash`, list fixture `id`s, and supply `news`, `quotes` or `lineup` observations, each with matching `fixtureId`, `observedAt` and `source`. Then:

```sh
python3 scripts/pipeline.py enrich --evidence outputs/evidence.json \
  --supplement outputs/verified-observations.json --out outputs/evidence-refreshed.json
```

Quotes additionally require a unique `id`, bookmaker/region, decimal odds, `ruleSource` and typed `market` matching the exact event. The runner's `MARKET` schema defines `family`, `selection`, `line`, `period`, `teamId`, `playerId`, `rules` and `legs`. Builder prices must be the actual combined quote. Confirmed lineup observations require unique player IDs in `homeStarters` and `awayStarters`, an `id` and `status: "confirmed"`. Predicted lineups do not pass that check. Current provider lineup descriptions are preserved as evidence but are not automatically converted into confirmed bookmaker-compatible player IDs.

Freshness defaults are configurable operational checks, not predictive weights. A team-market lineup check can be deemed immaterial only with explicit sourced rationale; builder starting-role checks remain material. The validator checks references and structure, not whether a supplied news statement is true. The research lead verifies decisive facts.

## Cost measurements

`usage` records requested versus reported model separately. Missing token counts or backend identity stay null. A supplied dated rate table can estimate API token costs; it does **not** measure a Codex subscription bill. `compare-costs` requires different explicit run IDs and matching scope, frozen evidence and completed task coverage, permitting batching/routing changes.

Usage covers the instrumented subprocess calls, not every interaction in the surrounding chat, external enrichment worker or provider charge. Include those separately before making an end-to-end cost claim.

```sh
python3 scripts/pipeline.py compare-costs --baseline outputs/baseline/manifest.json \
  --candidate outputs/optimised/manifest.json --rates outputs/verified-api-rates.json
python3 scripts/pipeline.py record-measurement --id comparison-001 --report outputs/comparison.json
```

The rate format is `{ "currency": "USD", "rates": [{ "model": "REPORTED_MODEL", "effectiveFrom": "YYYY-MM-DD", "inputPerMillion": NUMBER, "cachedInputPerMillion": NUMBER, "outputPerMillion": NUMBER }] }`. Optional `effectiveTo` closes a rate interval. Retrieve current official rates before filling it. No prices or savings are invented. Local manifests and clocks are trusted records, not tamper-proof billing evidence. Synthetic test token counts never establish real savings.

## Forecast evaluation

Register a protocol **before** its future observation window, defining scope/statuses, the baseline, primary metric, minimum paired observations and distinct fixture clusters. `football_pipeline/protocol.py` specifies the accepted fields. Record each genuine probability and its method (`probabilitySource`) before kickoff. A paired baseline forecast must be recorded for the same event and settlement definition. Ordinary result and promotional settlement are kept separate.

```sh
python3 scripts/pipeline.py register-protocol --spec outputs/future-protocol.json
python3 scripts/pipeline.py evaluate --protocol journal/protocols/PROTOCOL_ID.json
```

The report includes Brier/log-loss scores, coverage, calibration summaries and paired uncertainty clustered by fixture. It withholds a superiority conclusion when the pre-registered window, sample, complete outcomes or paired evidence are insufficient. Even a supported result concerns the recorded protocol cohort, not a universal profitable edge. This pipeline's qualitative decisions deliberately leave probabilities null unless a separate defensible forecasting process supplied them. The historical winning groups cannot fill that gap.

## Keep prompts lean

Code handles fetching, cache, scope, arithmetic and bookkeeping. Workers receive only their assigned fixture evidence and short stage-specific instructions; they do not inherit the long chat, every skill reference or all historical reports. The active lead reads relevant skill references once, verifies the important evidence and can reject any automated draft. No fixed numerical football weights, hardcoded favourite thresholds or compulsory shortlist size were introduced.
