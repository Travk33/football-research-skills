# Capture, verify and learn

These are implementation specifications. The fourth skill and recurring automation do not exist yet. Existing research skills continue to work independently until the journal is implemented.

## Proposed fourth skill: football-journal

One skill with four modes avoids scattering archive rules across three research skills. It changes neither the lead model nor app settings automatically. Its core instructions should remain concise, with the contract, examples and market settlement cases in references. Build and validate it with the skill-creator workflow when phase 3 begins.

### Capture

Input is the current research conversation, an explicitly named accessible conversation, or named saved reports. If asked to retrieve another chat, use the available chat retrieval tool and confirm which report was actually read. A skill cannot assume access to every private chat or reconstruct missing assistant analysis from the user's praise.

1. Identify date, category, fixture IDs, exact markets and original status. Read the relevant finished report and its supporting sources. Separate a direction from an approved price decision.
2. Extract reasons, counterarguments, conditions, source-backed facts, sample sizes, price observations and genuine forecasts. Record missing information explicitly. Important rejected games can be included as passes, but scope/counts must reflect what was imported.
3. Retain timestamps and provenance; a retrospective import remains historical. Never infer placement, stake, payout or a winning accumulator from a list of predictions.
4. Produce valid canonical JSON, check stable identities, and show a concise change summary. Repeat capture of unchanged material is a no-op.
5. Regenerate the index and save to the repo within the authorized scope. Read back counts and key fields. Publish only sanitized public data; keep full private evidence local.

The three existing research skills can later end with an optional handoff: “Save this completed ledger with football-journal when requested or when the user has enabled that workflow.” They must not silently reinterpret archival work as new prediction research. Add integration instructions only after the archive skill and validation exist.

### Refresh

Recheck a particular shortlist before kickoff. Append fresh prices, lineup evidence and decision changes as a new snapshot. Preserve v1; store why the new decision changed. A pass promoted after a result cannot become a pre-match selection. Unmet conditions stay conditional. A changed threshold/player/side creates a linked new selection.

### Verify

Use a lower-cost worker for bounded source retrieval and structured extraction. Let deterministic code apply supported market rules and a stronger reviewer resolve ambiguity.

1. Read the recorded contract before searching. Check the correct fixture, competition, venue, date and period.
2. Confirm match status. Prefer official competition/club results for scores; for player counts use the specified settlement provider where available. Cross-check material discrepancies; copied feeds are not independent corroboration.
3. Retrieve only facts needed by the recorded market. Win/BTTS needs score and period; eligible early payout may need the score timeline; SOT needs the named player's official/stat-provider count and participation rules.
4. Record source URL, provider, observed fact, publication/access times and limitations. If only a previous audit is available, label documented, not freshly verified.
5. Evaluate ordinary outcome separately from promotion application and actual settlement. Apply the cases below. Append a verification record; do not edit pre-match reasoning.
6. Validate and rebuild the manifest. A disputed or unsupported case stays needs-review. A missing page is not proof a selection lost.

### Review

Review a defined cohort after facts are verified, preferably weekly rather than rewriting skills after every game. Include both successes and failures and the exclusions that were recorded. Ask: was the data accurate, did the key condition hold, did the predicted mechanism occur, was the price acceptable on pre-match information, and what alternative explanation fits?

Tag observations such as small sample, opponent adjustment, rotation, player minutes, red-card distortion, provider disagreement, finishing variance, missing quote or settlement ambiguity. Distinguish a result from process quality. A narrow win does not automatically indict the method, and a win caused by an early red does not prove a pre-match tactical story.

Output a short proposed change with supporting records, counterevidence, affected skill section and prospective test. A stronger lead approves/rejects the patch. Record old/new method versions and the future evaluation window. The result worker must not automatically edit forecasting skills, tune thresholds to the winning examples, or announce that three slates prove an edge.

## Settlement cases the future skill must pass

These are fictional tests, not claims about archived matches.

| Recorded contract and facts | Required outcome |
|---|---|
| Team A FT win; A leads 2–0, finishes 2–3; eligibility confirmed | Ordinary lost; promotion-aware won; actual payment unknown without receipt |
| Same timeline, eligibility unknown | Ordinary lost; trigger occurred; promotion needs-review; no claimed payout win |
| A wins 3–2, only FT score available | Ordinary won; two-goal trigger unknown |
| A scores at 10, opponent at 20, A at 30, opponent at 40, A at 90 | A wins 3–2; max lead 1; no two-goal trigger |
| A's apparent second goal disallowed | Reconstruct validated score; do not use the overturned 2–0 display |
| Builder: eligible A win + A 6+ corners; A leads 2–0 but gets 4 corners | Result leg may win early; corners leg loses; builder loses |
| BTTS Yes; A leads 2–0 and wins 2–0 | BTTS loses; result promotion does not apply to BTTS |
| Under 4 Asian; match has 4 goals | Push under that verified contract |
| Under 4 three-way; match has 4 goals | Lost, not push |
| Over 5 corners three-way; count is 5 | Lost |
| Player prop; player does not start or gets substituted | Read exact participation/replacement rules; no guessed void or inherited substitute stats |
| Match postponed or abandoned | Check contract rules; pending/needs-review until known, never automatic loss |
| Named-provider SOT count changes from 1 to 0 | Superseding verification with correction evidence; preserve old observation |
| Winning entry originally marked pass | Winning counterfactual result; original pass retained and excluded from selected cohort |

Current UK bet365 offer material describes qualifying result selections and a two-goal trigger; in builders/multiples the other conditions still have to succeed. Eligibility depends on the actual market, competition, timing and offer terms. Store the relevant dated rule reference and recheck it when used rather than generalizing across every selection. [Official offer](https://www.bet365.com/promos/en-gb/home/early-payout-offer).

## Proposed scheduled verification

Recommendation: one **09:00 Europe/London** run daily, after the previous day's games. This is a design recommendation, not an enabled automation. Start with one manual dry run once the site/skill exist. Configure the actual model and schedule through the app's automation tool when the user asks to enable it; do not invent a configuration file that claims to schedule the app.

The scheduler reads a small queue of unresolved finished fixtures from the preceding 48 hours plus explicitly queued older corrections. It exits quietly if there is no work. Cap a run at 20 fixtures, use a maximum of two targeted retrieval attempts per unresolved fact, and queue overflow for the next run. Retry missing statistics once the next day; keep persistent failures visible for review. Do not retry all historical games forever or rescan already verified matches every day. A known correction or newly supplied evidence can reopen a record.

Draft task instructions for later scheduling:

```text
Use football-journal in verify mode in the football-research-skills project.
Read the recorded unresolved-results queue. Verify only finished fixtures from the last 48 hours and explicitly queued corrections; max 20 fixtures per run. Exit without a notification when there is no work.
Use the configured Luna model for bounded retrieval and structured extraction. Apply supported rules with the journal's deterministic validation/evaluation code. Do not make new predictions or alter research decisions. Respect source-specific player counts, exact periods and market rules. Keep FT outcome, promotion eligibility/trigger, rule-based outcome and actual settlement separate. Do not infer a two-goal lead from final score alone.
Append evidence-linked verification records, preserve conflicting sources and flag unresolved cases. Repeat retrieval at most twice now and once the following day; then queue for review. Validate all changes and regenerate the index. Keep private account information out of the public repo. Save changes within the automation's configured scope; only push if that scope includes repository publishing. Notify only about new verified results, corrections, failures or review needs, with a compact summary. Do not modify the research skills or take bookmaker actions.
```

Do not promise automatic escalation unless the automation environment actually supports the specified worker/model route. If unavailable, leave a review item for the lead. A failed save/push must be reported distinctly from a failed sports-data verification. Record run ID/time, model used, changed records, source failures and queue remainder.

## Model allocation

| Work | Suggested model/effort | Boundary |
|---|---|---|
| Implement the finished static site | GPT-6.1 Sol / High | Own integration, inspect mobile/desktop and fix defects |
| Bounded historical extraction | GPT-6 Luna / Medium | Small named reports, fixed schema; no invented missing facts |
| Routine result retrieval | GPT-6 Luna / Medium initially | Escalate effort if extraction quality needs it; rule evaluation remains deterministic |
| Focused contract/visual review | GPT-6.1 Sol / High | Challenge one completed artifact against acceptance cases |
| Research judgments and method changes | Selected strong lead; Astra High/Extra High for demanding work | Resolve conflicts and approve prospective method revisions |

These are our workflow choices, not measured football-accuracy rankings. Official guidance positions Sol for capable work with lower cost than Astra and Luna for focused extraction/repeatable tasks. Model availability and efforts depend on the client. [Official model guidance](https://learn.chatgpt.com/docs/models).

Explicitly set worker model and effort where supported. Defaults can inherit the lead; a skill is not an automatic inexpensive router. Use bounded context for retrieval workers and have the lead audit decisive evidence. [Official subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).
