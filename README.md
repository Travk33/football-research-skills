# Football research skills

Three football research skills and one journal/review skill. They produce auditable shortlists, explicit passes and preserved decisions. Forecasting performance remains to be established prospectively.

**Read first:** [brief skill map](SKILL-MAP.md). Each skill below also has a short human-readable README; `SKILL.md` contains its full operating instructions.

| Read first | Full instructions | Use it for |
|---|---|---|
| [Wins / BTTS guide](skills/football-wins-btts/README.md) | [football-wins-btts](skills/football-wins-btts/SKILL.md) | Match winners and BTTS; this project's future suggestions use BTTS Yes only |
| [Other markets guide](skills/football-other-markets/README.md) | [football-other-markets](skills/football-other-markets/SKILL.md) | Goal totals, team totals, handicaps, corners and cards |
| [Bet builders guide](skills/football-bet-builders/README.md) | [football-bet-builders](skills/football-bet-builders/SKILL.md) | Compatible selections within a fixture, with actual market availability and joint price |
| [Journal guide](skills/football-journal/README.md) | [football-journal](skills/football-journal/SKILL.md) | Archive decisions, verify outcomes and review specific lessons |

The methods keep football evidence, numerical forecasts, offered prices and settlement separate. A successful result does not retrospectively convert a price pass into an approved selection. Results are reviewed against original decisions, and proposed improvements are evaluated prospectively.

## Use

For complete copy-and-paste prompts, model-picker instructions and the matchday workflow, see [USAGE.md](USAGE.md).

Copy each desired folder from `skills/` into `${CODEX_HOME:-$HOME/.codex}/skills/`. The folders are self-contained. Do not overwrite personal modifications without reviewing them. Start a new chat if the newly installed skills do not yet appear in the current session's catalog.

Example requests:

- `Use $football-wins-btts to screen Saturday's major European leagues. Research both teams, compare prices and retain passes.`
- `Use $football-other-markets to compare goals and corners for today's internationals. Verify integer-line settlement.`
- `Use $football-bet-builders for two picks per Nations League A match. Check starters, minutes, exact player lines and actual combined quotes. Do not force a pair where evidence is weak.`

## Models and efficient delegation

See the bundled [model routing guide](skills/football-bet-builders/references/model-routing.md). Use a cheaper model for bounded extraction; retain a stronger lead for source conflicts, tactical reasoning, pricing judgments and final selection. A skill is a procedure, not a model upgrade, and it does not automatically change the active model or guarantee equal reasoning quality.

Default routes: **GPT-6.2 Astra / High** for lead analysis, **GPT-6.2 Sol / High** for independent review, and **GPT-6 Luna / Extra High** for bounded retrieval where available. Disclose unavailable routes and any explicit override; never silently substitute a more expensive worker.

The same routing guide is included in each skill so each installation remains independent. Keep those copies synchronized when updating it. Availability and pricing must be checked in the current environment rather than assumed from this repository.

## What gets checked

Date/venue/fixture status; broader baseline and recent form; opponent quality; missing data; xG-provider consistency; red cards and penalties; current availability; player minutes and role; tactical opportunity; exact event definition; price timestamp; correlated legs; counterarguments; and criteria for passing.

The methods do not require expensive modeling for every task. They do require honest labeling: a descriptive hit rate, an illustrative model and a calibrated forecast are different outputs. Fair odds or a positive expected-value claim require a declared forecasting method and uncertainty assessment.

## Journal and implementation status

The [local JSON journal](journal/README.md), append/validation scripts and fourth archive/review skill are implemented. [Active lessons](journal/active-lessons.md) feed subsequent research. The [earlier UI design](design/journal/README.md) remains a design artifact; no journal UI or recurring checks are enabled.

The [scoped research pipeline](pipeline/README.md) now implements variable-size fixture collection, a shared cache, explicit model routing, bounded staged screening, journal archiving and usage/evaluation reports. Its scope follows the requested dates and competitions, teams or fixtures. Material news, player and bookmaker observations still require source verification and enrichment through the active research skill. Model drafts do not replace the lead's judgment.

The tools measure observed usage and support comparable-run cost estimates and prospective evaluation. They do not establish a whole-workflow saving percentage or forecasting superiority from the historical journal. See [implementation validation](pipeline/VALIDATION.md).

## Validation and review

Skill frontmatter and references are checked during packaging. [Behavioral cases](validation-cases.md) capture common decision errors for independent review. The journal also has executable integrity tests. These checks assess workflow and record integrity, not historical profitability. Research archives contain source-linked reports and public match-data snapshots; actual bookmaker settlement is tracked separately and remains unknown where unverified.
