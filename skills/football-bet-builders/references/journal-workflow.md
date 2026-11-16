# Journal workflow

Apply on every research, refresh and result-review run. Read the active project's AGENTS.md and journal/README.md first. In AI-Bets the maintained store is journal/data/events and the helper is scripts/journal.py. Read journal/active-lessons.md and the relevant recent reviews before making decisions; past wins are not evidence for a new pick.

## Record before delivering the shortlist

Use the project's event helper and schema rather than editing old event files. Record each researched direction and important pass/reserve, exact market/period/line, quoted terms and time, source report, evidence, strongest countercase, unmet conditions, and a forecast only when genuinely modeled. Reference the full fixture inventory so missing and shallow coverage stay visible. Preserve original status, including zero final selections.

If a slate produces no decision rows, append a `review` with `decisionIds: []`, `matchDate`, `category`, and the report or inventory in `source`. Record the zero final selection count and reason in `note`.

Choose prospective only for actual capture before kickoff. Historical imports use the true import time and a separate originalTime/provenance; never backdate capture. Do not infer original approval, accepted prices or placement from winning outcomes. Reuse stable source-entry IDs to avoid duplicating imports.

Record status changes as new events with new evidence and a reason. Clear material football, lineup, price and contract questions before selection; an ideal XI alone cannot resolve weak evidence or unattractive terms. A changed side, threshold or player is a linked new decision, not a rewrite. The CLI rejects late prospective capture and promotions appended at or after kickoff across all cohorts.

## Verify and learn

Append sourced outcomes separately from decisions. Keep ordinary statistical outcome, promotion trigger/eligibility, rule-based result and actual bookmaker settlement distinct. Record unknowns and source conflicts. A 2-goal trigger does not settle BTTS/corners/player legs; builder legs and participation rules remain independent requirements. Actual settlement needs receipt evidence, not a scoreline.

Review wins, losses, candidates, reserves and recorded passes; show them in their original cohorts. A losing candidate still deserves a process review even when no final bet was approved. Newly retrieved historical evidence belongs in the review with its retrieval time, not backfilled into the old forecast.

For a method change record the failure mechanism, evidence and counterevidence, affected markets, old/new method version, and a future evaluation plan. The lead decides changes; a retrieval worker must not tune the skill automatically to the latest winner or loser. Keep historical imports and prospective performance separate. Do not derive a forecast from break-even odds or claim ROI from incomplete tickets.

Run the project validator after appends and report the journal/report paths. A failed save means archiving is incomplete: disclose it and preserve an export without claiming success. If another project has no configured journal, preserve a dated local decision ledger and state the gap; do not silently use AI-Bets' history or overwrite another project's archive. No UI, automation, remote publication or bookmaker transaction is implied by journaling.

