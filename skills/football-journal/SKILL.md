---
name: football-journal
description: Archive football research decisions, verify recorded outcomes, and review methodological lessons in a project's local JSON journal. Use for record keeping and post-match audits, not new betting selections or bookmaker transactions.
---

# Football journal

Read the active project's AGENTS.md, journal/README.md, journal/active-lessons.md and the relevant research reports. Use the project's schema and scripts/journal.py. Preserve the user's market exclusions in new suggestions while retaining historical excluded markets for honest review.

Determine whether the task is archive, verify or review; combine only the requested work. No UI or scheduled job is implied. Never claim a chat was read unless retrieved or supplied; saved reports and pasted text have their own provenance.

## Archive

Record the original exact direction and research status, timestamp precision, source report, odds observation, market definition, evidence, countercase, conditions and genuine forecast or null. Preserve candidate/reserve/pass and final distinctions. Capture every new slate before kickoff, including zero final selections, plus important exclusions and a link to the coverage inventory.

If a slate produces no decision rows, append a `review` with `decisionIds: []`, `matchDate`, `category`, and the report or inventory in `source`. Record the zero final selection count and reason in `note`.

Use true current capture/import time. Retrospective material belongs in historical-import, with separately attributed original time; unknown remains null. Keep actual user tickets separate from research. A selected research direction does not verify placement.

Use stable source-entry IDs and append-only CLI operations. Original decisions are not edited. Revisions need evidence, time and a reason. Append promotions before kickoff across all cohorts. Changed market contracts create new linked decisions.

## Verify

Read the recorded contract first. Retrieve final status and the facts required by that contract from official results or a clearly named statistics provider. Check fixture identity and period. A live snapshot is not FT. Keep source conflicts and corrections; new verification supersedes an old outcome explicitly.

Separate on-pitch outcome, rule-based result, two-goal trigger and promotion eligibility, and actual account settlement. A promotion applies only to its eligible leg. Player participation, replacement and void rules require their own contract. Unknown eligibility or unavailable quotes must not be filled from inference. Do not store private receipts or credentials in the repository.

## Review

Assess process separately from outcome. Read original supporting evidence and counterarguments before using results to explain the decision. Check whether material conditions were closed, whether the mechanism held and what game-state events changed it. A winning reserve remains a reserve, and a losing conditional candidate remains worth auditing.

Newly retrieved pre-match historical statistics must be labeled retrospective retrieval, not inserted into the original evidence record. Include successes and failures, rejected alternatives and data gaps without rewriting history. Historical imports do not enter prospective performance totals.

Record proposed or adopted method changes as events with supporting records, counterevidence, scope, version and a future evaluation window. Read the research skill's evidence-quality/review references when changing its method. The reasoning lead owns changes; a result-retrieval worker does not rewrite prediction skills automatically.

## Tools, roles and completion

Use a cheaper bounded retrieval worker where supported by current project routing, deterministic code for arithmetic/validation and a capable lead for disputed evidence and methodological conclusions. Report actual model routes when material. Do not invent a model switch or automation.

Run scripts/journal.py validate and summary after updates. Report saved paths, what was verified, unresolved facts and any save failure. Summary keeps original-status outcomes visible and final-selection performance separate. No ROI or calibrated edge is established by raw hit rates. Do not place bets or publish the repository unless separately authorized in the task.

