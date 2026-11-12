# Football research skills

Three reusable Codex skills for evidence-led football analysis. They produce auditable shortlists and explicit passes, not guaranteed winners or a demonstrated betting edge.

| Skill | Use it for |
|---|---|
| [football-wins-btts](skills/football-wins-btts/SKILL.md) | Match winners and both teams to score across domestic leagues, European cups and internationals |
| [football-other-markets](skills/football-other-markets/SKILL.md) | Goal totals, team totals, handicaps, corners and cards |
| [football-bet-builders](skills/football-bet-builders/SKILL.md) | Two or three compatible player/match selections within a fixture, with actual market availability and joint price |

The methods keep football evidence, numerical forecasts, offered prices and settlement separate. A successful result does not retrospectively convert a price pass into an approved selection. Recent results are reviewed prospectively rather than used to justify longer accumulators.

## Use

For complete copy-and-paste prompts, model-picker instructions and the matchday workflow, see [USAGE.md](USAGE.md).

Copy each desired folder from `skills/` into `${CODEX_HOME:-$HOME/.codex}/skills/`. The folders are self-contained. Do not overwrite personal modifications without reviewing them. Start a new chat if the newly installed skills do not yet appear in the current session's catalog.

Example requests:

- `Use $football-wins-btts to screen Saturday's major European leagues. Research both teams, compare prices and retain passes.`
- `Use $football-other-markets to compare goals and corners for today's internationals. Verify integer-line settlement.`
- `Use $football-bet-builders for two picks per Nations League A match. Check starters, minutes, exact player lines and actual combined quotes. Do not force a pair where evidence is weak.`

## Models and efficient delegation

See the bundled [model routing guide](skills/football-bet-builders/references/model-routing.md). Use a cheaper model for bounded extraction; retain a stronger lead for source conflicts, tactical reasoning, pricing judgments and final selection. A skill is a procedure, not a model upgrade, and it does not automatically change the active model or guarantee equal reasoning quality.

The same routing guide is included in each skill so each installation remains independent. Keep those copies synchronized when updating it. Availability and pricing must be checked in the current environment rather than assumed from this repository.

## What gets checked

Date/venue/fixture status; broader baseline and recent form; opponent quality; missing data; xG-provider consistency; red cards and penalties; current availability; player minutes and role; tactical opportunity; exact event definition; price timestamp; correlated legs; counterarguments; and criteria for passing.

The methods do not require expensive modeling for every task. They do require honest labeling: a descriptive hit rate, an illustrative model and a calibrated forecast are different outputs. Fair odds or a positive expected-value claim require a declared forecasting method and uncertainty assessment.

## Validation and review

Skill frontmatter and references are checked during packaging. [Behavioral cases](validation-cases.md) capture common decision errors for future independent review. These checks validate workflow instructions; they are not a historical profitability backtest. No private account data, personal stakes, screenshots or bulk source datasets are part of this repository.
