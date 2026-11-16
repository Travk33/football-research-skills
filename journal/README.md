# Football journal

This local event journal preserves the original research decision and appends changes. It is not a bookmaker account, a settlement engine, or proof a bet was placed. Historical imports remain separate from prospective records. Do not store receipts, secrets or private paths here; use a sanitized receipt evidence note if an actual settlement is known.

```sh
python3 scripts/journal.py init
python3 scripts/journal.py add /path/to/event.json
python3 scripts/journal.py validate
python3 scripts/journal.py summary
```

Use `--dir /path/to/data` before the command for an isolated store. Each event is a UTF-8 JSON object, saved as `data/events/<id>.json`. IDs are stable safe filenames, assigned by the author. `add` validates the whole store and writes and syncs a temporary file then publishes it atomically without replacing a file; an identical ID and content is a no-op, while a changed duplicate is an error. Cooperating CLI writers use a lock around validation and creation. Do not edit or delete event files to change a decision; append a revision or outcome. This is an operational convention, not a tamper-proof archive. Validate after copying files or changing tools. A corrupt event or broken reference fails the command instead of producing partial totals.

All event inputs require `schemaVersion: 1`, `id`, `type`, and `recordedAt` (source or claimed record time, ISO timestamp with timezone). The CLI assigns and persists `appendedAt` from its system clock; omit it when adding a new event. Identical replays remain no-ops, with or without the original assigned field. The system clock and filesystem are trusted, not cryptographic proof. `schema.json` describes the base structure; the CLI additionally enforces cross-event, chronology and numerical rules. Additional fields are permitted for detailed contracts, provenance and evidence. Unknown facts are null, not invented. Preserve sanitized report identity and source limitations. Use a stable `source.identity` unique to the source revision and individual entry; re-import the same entry with the same event ID and unchanged content.

A `decision` requires:

- `cohort`: `prospective`, `historical-import`, or `demo`; `matchDate`: ISO date; `category`: `wins-btts`, `other-markets`, or `bet-builders`.
- `fixture`: object with `home` and `away`; `market`: object with original `rawLabel` and boolean `resolved`. Include exact market rules, period, selected subject and builder legs when known.
- `status`: `candidate`, `conditional`, `watch`, `reserve`, `pass`, or `selected`; preserve the original wording in extra fields. A research direction is not automatically a selected bet.
- `source`: object with unique `identity` and `report` (which may be null); `originalTime`: object with `value` (ISO timestamp or null), `precision` (`exact`, `approximate`, `date-only`, `unknown`), and `preKickoffEvidence` (`verified`, `claimed`, `unknown`). Use null for an unknown exact timestamp; a date-only value belongs in an additional field, not as invented midnight.
- `kickoff`: ISO timestamp with timezone or null; `evidence`, `countercase`, `conditions`, `odds`, and `probability`, each null if unknown. Odds are decimal and greater than 1; probability is a genuine forecast in [0,1], not derived from odds. Preserve source prices and times in additional fields.

Every prospective decision must be appended before a known kickoff. A prospective `selected` decision requires exact verified pre-kickoff original and recording timestamps, a resolved market, price, and `conditions: "met"`. For a historical import, do not fabricate these to satisfy that prospective gate. A selected decision with a known original timestamp at or after kickoff is rejected.

A `status_revision` requires `decisionId`, `status`, `effectiveAt` (ISO timestamp), and `reason`. Its original remains intact. A selection must be effective and recorded before the known kickoff; a retrospective selection belongs in the original historical decision, supported by its source, rather than a late promotion revision. For a prospective promotion to selected, it must also be recorded before kickoff with `preKickoffEvidence: "verified"`, `conditions: "met"`, and decimal `odds` greater than 1; the original market must be resolved. Post-kickoff updates cannot promote a selection, and cannot affect pre-kickoff cohort membership, even if their claimed effective time is backdated. A prospective revision cannot be captured before its parent. Record changed market contracts as a new decision with a link to the old one. Corrections to historical transcription should be clearly described and must not be represented as prospective capture.

An `outcome` requires `decisionId`, `evidenceLevel` (`pending`, `documented`, `verified`, `disputed`), `onPitchOutcome`, `ruleBasedOutcome`, `bookmakerSettlement`, and `sources` (array). Documented and verified outcomes need at least one source. Use a nonblank string reference or an object with a nonblank `url`, `path`, or `reference`. Outcome record time must be at or after the parent capture. If kickoff is known, a resolved ordinary outcome must be recorded at or after it. A historical import with unknown kickoff can retain a documented or verified result with sources. Keep any earlier historical observation time in a separate field.

Outcome values are `won`, `lost`, `push`, `void`, `half-won`, `half-lost`, `pending`, `unknown`, or `needs-review`. A bookmaker settlement value other than `unknown` requires a nonblank, sanitized `receiptEvidence` note about the operator's settlement. Keep ordinary, promotion-aware and actual settlement separate. Record a correction as a new outcome with `supersedesId`. Independent agreeing outcomes resolve to their shared ordinary outcome. Conflicting or disputed outcomes require review. Never infer a two-goal lead from the final score.

A `review` or `method_change` requires `decisionIds` (possibly empty) and `note`. Append the evidence, alternative explanation, approval and future test as appropriate. These events preserve the decisions they reference. For a slate with no decision rows, append a `review` with `decisionIds: []`, `matchDate`, `category`, and the report or coverage inventory in `source`. Record that the final selection count was zero and why in the note.

`summary` separates cohorts and counts the latest status with effective, claimed record, and tool append times all before kickoff per decision. Its results count only selected decisions, once per decision, using ordinary on-pitch outcomes. Missing results are pending, disputed or conflicting results need review, and binary hit rate is wins divided by wins plus losses; pushes, voids, halves and unresolved results remain outside that denominator. Selected total and binary resolved count expose coverage. Demo and historical imports never enter prospective totals. No ROI is computed. The journal does not independently verify sports results, exact market contracts, sources, or pre-kickoff evidence; the author must supply and check them. The cutoff uses recorded scheduled kickoff; uncertain actual kickoff and rescheduled fixtures require manual review.

The separate `directionalOnPitchOutcomes` breakdown groups every decision by category, original status, effective pre-kickoff status, and ordinary outcome. It includes passes, candidates, conditional picks, watches, and reserves as counterfactual research directions; these are not selected performance or proof of bets. Conflicted or missing results remain needs-review or pending.

## Initial archive, 15 November 2026

The initial import contains **69 historical research directions, 69 outcome records, seven reviews and one method change**. These are not 69 placed bets or 69 final selections. Conditions were not independently documented as closed, and no actual account settlement or calibrated probability has been inferred. The tool assigned the real November 15 append times; separately preserved original times have their own precision and source.

| Match date | Directions | Coverage |
|---|---:|---|
| 5 November | 8 | Seven directions from the user-reported successful group plus the failed Monaco watch |
| 7 November | 6 | The discussed Saturday group, retaining material conditions |
| 8 November | 6 | The five discussed directions plus omitted Brighton; preserves reserves and Utrecht price pass |
| 12 November | 13 | Nine result/total/corner directions and four provisional builder pairs |
| 13 November | 19 | Five discussed conditional directions, important alternatives/reserves/passes and three exploratory player directions |
| 14 November | 17 | Winner and BTTS Yes screens across all eight Nations League fixtures; both winner directions for Northern Ireland–Ukraine; zero final selections |

The full reports retain broader screened fixtures not individually imported from every earlier chat. In particular, the November 13 outside-UEFA screen is wider than its imported important reserves/passes. This is a bounded historical reconstruction, not an assertion that every past message or market has been recovered. Builder outcomes describe statistical thresholds; starter/void/promotion terms and actual settlement remain separate. McGinn's two lines are related alternatives, not independent observations or a pair.

[`active-lessons.md`](active-lessons.md) contains the instructions for future research. The [November 14 review](../research/2026-11-14/post-match-review.md) explains the latest findings and limits. `scripts/import_initial_journal.py` reconstructs this archive through the same journal writer. It uses stable identities and original capture times on replays; identical reruns are no-ops, while changed inputs fail rather than overwrite. Add new dates with the normal event workflow, not by relabeling these imports as prospective.
