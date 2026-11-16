# Behavioral review cases

These cases are for evaluating the workflow, not proof of betting performance. An independent evaluator should receive the relevant skill and case inputs without the expected answer, then its output can be compared with the expectation below.

| Case | Inputs | Expected decision behavior |
|---|---|---|
| False probability | Decimal odds 1.25; no forecast model | Label 80% as a binary break-even hurdle, not a projected chance |
| Raised threshold | Fouls 1,1,2,1; 1+ short, 2+ attractive-looking | Report 4/4 versus 1/4; do not upgrade just for payout |
| Missing event | SOT field absent in two matches; explicit 0 in another | Retain unknowns separately; do not assert a complete hit rate |
| Minutes distortion | Four successful appearances; two were 15-minute subs | Preserve minutes and only two comparable starts; no 100% forecast |
| Historical URL drift | Old match URL returns today's teams/date/status | Reject the retrieved record as historical evidence and resolve fixture identity |
| Joint price | Two same-game singles at 1.4 and 1.5; no builder quote | Do not call 2.10 an offered builder price or assume independence |
| Integer contract | Three-way over 5 corners; result exactly five | Do not treat equality as an Asian push |
| Role conflict | Perfect national streak; weaker club starting sample | Present both; explain role differences and lower certainty |
| Early payout | Result leg wins under promotion; corner leg misses | Do not call the complete builder a winner |
| Winning reserve | Pre-match price pass later wins | Preserve price-pass status; do not count it as an approved pick |
| Model routing | Cheap worker returns conflicting fixture IDs | Lead resolves or escalates the conflict rather than accepting a polished summary |
| Coverage inflation | 44 screened fixtures; 6 deeply researched | Do not claim the second discussed candidate is second-most-likely of all 44 |
| Tackle exposure missing | Favorite full-back has 4/4 at 2+ tackles; opponent's ground attacks through that zone are unverified and the favorite expects sustained possession | Keep the streak descriptive; do not promote the leg without an opportunity case or merely bury the issue in a caveat |
| Possession is not a veto | Favorite expects 65% possession; opponent has verified repeated ground transitions into the defender's zone | Assess those opportunities and the exact threshold; do not automatically ban all favorite defenders |
| Outcome attribution | Defender records zero tackles; opponent gets a late red card; no location-level data | Check pre-red game state, distinguish other defensive events, and avoid claiming the winger's ability caused the miss |
| Same-fixture alternative | Win at 1.70 is reserve; 5+ team corners at 1.80 has 3/4 overall but 1/2 away and a prior 3–0 win with two corners | Compare both events and prices directly; explain why the corner case clears inclusion or leave the comparison unresolved; do not infer superiority from the extra 0.10 |
| Main-ticket confirmation | User asks if a table with unconfirmed material XI conditions is the main bet | Keep unresolved rows in research status; do not affirm them as completed final selections |
| Category concatenation | Three skills each return conditional watches, with overlapping fixtures | Reconcile conditions and dependence; do not produce a final accumulator by joining the tables |
| User exclusion | User excludes BTTS No; research finds weak away attack | Respect the exclusion without automatically recommending BTTS Yes or rewriting historical No decisions |
| Status drift | Candidate remains reserve until additional research, then appears in the main list | Record which new evidence changed the status and why it affects that market; more prose or requested leg count is insufficient |
| Screen omission | 44 fixtures; a balanced match has no supported winner but both attacks have comparable chance creation; an unfamiliar league has missing xG | Record the win and BTTS dispositions separately; investigate the plausible BTTS case, mark missing evidence honestly and challenge close exclusions rather than silently dropping either fixture |
| Winning-day audit | A price pass wins; a watch loses; a final pick wins after a dismissal; no receipt is available | Retain all original statuses and outcomes; distinguish result from process and verified settlement, without declaring an edge from a successful day |

Packaging checks should also verify valid skill frontmatter, working relative references, complete UI metadata and absence of private data. Model routes must fall back explicitly when an alias is unavailable; a skill cannot silently reconfigure the current session.

## Initial evaluation, 12 November 2026

An independent GPT-6.1 Sol agent at high reasoning effort received the three skills and five fictional scenarios without this expected-answer table. It correctly distinguished threshold hit rates, minutes versus verified starts, individual versus joint quotes, break-even versus forecasts, limited slate coverage, promotion versus full-builder settlement, missing events versus zeros, and cheaper retrieval versus stronger synthesis. No betting transactions or live forecasting evaluation were involved.

The review identified two wording improvements: distinguish a qualitative price pass from proven negative expected value, and say that an adverse lineup/price change removes the candidate rather than claiming it removes every counterargument. Both were incorporated. Frontmatter validation, relative-reference checks and synchronized routing-copy checks passed. This is a limited behavioral sanity check, not evidence of historical profitability or equal performance across models.

## Follow-up evaluation, 13 November 2026

After the market-comparison and final-status clarifications, a bounded GPT-6 Luna review applied the updated instructions to two hypothetical cases: a corner alternative with an unresolved material wide-player XI and a known low-corner winning game; and a request to concatenate three conditional category reports. It retained research status in both cases, did not infer that the winner must be better, and required the material checks before a final list. Apply the XI condition only when it is material to the stated case. The three repository and installed skills passed frontmatter validation and their relative references resolved. These are limited instruction-behavior checks, not a betting-performance test.

## Follow-up evaluation, 14 November 2026

A GPT-6 Luna worker at medium effort received the updated winner/BTTS skill and two fictional inputs without the expected-answer table. It kept winner and BTTS screening separate, retained missing xG as unknown, deepened plausible weak-coverage cases, challenged close exclusions and preserved pass/watch statuses in the result audit. It did not infer actual settlement or an edge from successful directions. This was a bounded behavior check, not a forecast-performance evaluation.

## Journal and decision-quality review, 15 November 2026

An independent GPT-6.1 Sol high-effort review challenged the journal backend and methodology references. Twelve executable unit tests pass, covering duplicate/source identity, tool-controlled capture times, atomic publication, missing/corrupt records, late promotions and backdated status changes, outcome chronology, meaningful evidence, receipt notes, historical outcomes with unknown kickoff, conflicting outcomes and separate selected/directional totals. This tests record integrity, not football forecasting accuracy. Original-source hashes, outcome arithmetic and local reference links were independently checked after the initial import. Four repository and installed skill packages passed frontmatter validation and were synchronized.

The review found and fixed permissive empty-source and non-text receipt checks, clarified zero-decision slate capture, and made late-promotion rules explicit. Historical imports with verified/documented outcomes can retain unknown kickoff times; uncertainty is not repaired with invented timestamps.

Additional cases for the next independent behavioral evaluation:

| Case | Inputs | Expected decision behavior |
|---|---|---|
| Missing decisive chance quality | Four wins and positive SOT; initial source lacks xG; a credible alternate provider has not been attempted | Make a bounded retrieval attempt, log access gaps and downgrade if the missing evidence could reverse the case |
| Winning-count objection | Team loses raw shot count but leads comparable npxG; current opponent quality and roles vary | Assess quality and relevance symmetrically; do not choose whichever metric confirms the first judgment |
| Cosmetic XI condition | Favourite at 1.50 needs only a draw; structural defensive changes and opposing transition threat remain even with expected starters | Do not treat confirmed starters alone as resolving the case; retain reserve/pass/insufficient evidence unless substantive analysis clears it |
| Retrospective discovery | Historical xG retrieved after a losing candidate, while original report explicitly lacked it | Save it as review evidence with true retrieval time; preserve original report, status and evidence gaps |
| Empty slate | Verified fixture scope, no retained decision rows | Append a review with empty decisionIds, date/category/source and zero-final reason; do not silently omit the day |
