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

Packaging checks should also verify valid skill frontmatter, working relative references, complete UI metadata and absence of private data. Model routes must fall back explicitly when an alias is unavailable; a skill cannot silently reconfigure the current session.

## Initial evaluation, 12 November 2026

An independent GPT-6.1 Sol agent at high reasoning effort received the three skills and five fictional scenarios without this expected-answer table. It correctly distinguished threshold hit rates, minutes versus verified starts, individual versus joint quotes, break-even versus forecasts, limited slate coverage, promotion versus full-builder settlement, missing events versus zeros, and cheaper retrieval versus stronger synthesis. No betting transactions or live forecasting evaluation were involved.

The review identified two wording improvements: distinguish a qualitative price pass from proven negative expected value, and say that an adverse lineup/price change removes the candidate rather than claiming it removes every counterargument. Both were incorporated. Frontmatter validation, relative-reference checks and synchronized routing-copy checks passed. This is a limited behavioral sanity check, not evidence of historical profitability or equal performance across models.
