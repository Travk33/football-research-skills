# Using the three football research skills

## Choose the lead in Codex

Use **GPT-6.2 Astra / High** for lead analysis and **GPT-6.2 Sol / High** for independent review. Keep **GPT-6 Luna / Extra High** for bounded retrieval where available. These are the project defaults, not validated differences in football prediction performance. [Official 6.2 guidance](https://learn.chatgpt.com/docs/whats-new/gpt-62-astra-sol).

Select **GPT-6.2 Astra** and **High** under the composer before sending the prompt; prefer Standard speed for the cost-conscious workflow. A skill cannot switch the active lead or app settings. Higher effort or a different lead is an explicit override, not an automatic escalation.

Explicitly select worker models and effort. Unconfigured subagents can inherit the lead's settings. If Luna or another requested route is unavailable, disclose that limitation and record any explicitly chosen alternative; never silently substitute a more expensive worker. Availability can differ between the chat subagent menu and the pipeline's CLI. [Subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Start a request

For shared collection and bounded model execution, the project now provides [scripts/pipeline.py](scripts/pipeline.py); see the [pipeline guide](pipeline/README.md). Ask the chat to translate your actual fixture scope, reuse the cache, report coverage and resolve material gaps before final decisions. There is no fixed 44-game scope. The code does not automatically access your bookmaker account or establish a prediction edge.

Use one new research chat per matchday in this project as an organizational default, then keep its lineup/price refresh in that same chat. A fresh chat does not improve football forecasting by itself. Carry forward the saved decision records and project preferences rather than a claim that an earlier winning streak proved the method.

Start with the market family you actually want. Run other markets or player builders as separate, explicitly scoped tasks when useful; they do not each need to produce selections. A separate builder chat is optional for a large task, not a prerequisite for accuracy. Share the same saved match evidence, and reconcile any same-fixture alternatives before forming a final list. Do not concatenate three category watchlists into an accumulator.

Project-specific exclusions belong in `AGENTS.md`; check them before each research run. Historical excluded markets remain in the audit record. General skill instructions do not turn a user's preference into a universal claim about a market.

1. Open a new Codex chat, preferably in the football research project so earlier reports are available when you ask for comparisons.
2. Choose GPT-6.2 Astra with High reasoning effort, unless explicitly overriding the default.
3. Replace `[DATE]` with a calendar date and any bracketed fixture field with your intended scope. Keep Europe/London if you want UK kickoffs. This avoids ambiguous “next Saturday” dates during international breaks.
4. Paste one prompt below. The installed skill is invoked with `$skill-name`. If it is not found, ask the agent to check its installed skill folder rather than claim it used it. [Skill invocation](https://learn.chatgpt.com/docs/changelog).
5. Review the shortlist, then request a fresh XI/price check when lineups are published. An early report remains conditional until its stated gates are satisfied.

## Prompt 1 — winners and BTTS

```text
Use $football-wins-btts and its relevant references for matches on [DATE], Europe/London.

Read AGENTS.md, journal/README.md and journal/active-lessons.md first. Consider wins and BTTS Yes only. Use scripts/journal.py to preserve candidates, important passes, final decisions and later changes; validate after saving.

Screen the men's top divisions in England, Spain, Germany, Italy, France, Netherlands, Portugal, Belgium, Scotland and Türkiye. Verify fixtures, actual venues, kickoffs and status. Research that day only and exclude matches already started.

Use gpt-6.2-astra at high effort as the selected lead (choose it in the model picker; the skill cannot switch it). Keep the lead responsible for methodology, tactical interpretation, conflicting evidence and final decisions. Where supported, explicitly use gpt-6-luna at extra-high (`xhigh`) effort for independent fixture/statistics/team-news retrieval and gpt-6.2-sol at high effort for a focused challenge of the final shortlist. Give workers bounded tasks, audit decisive evidence and report the models actually used. Disclose unavailable routes and any explicit alternative; do not silently substitute models.

Apply the full skill methodology. Compare both teams using a season or comparable competitive baseline and recent 5–10 relevant games where available, home/away context, opponent quality, xG/npxG where available, shots/SOT, availability, rest and tactics. Retain actual sample sizes, missing data and distortions from penalties, dismissals, own goals, rotation and extreme results. For winners, explain the opponent's scoring routes and draw risk; for BTTS Yes, establish a scoring route for each team separately.

Check current UK bet365 prices where accessible, otherwise identify the alternative source. Record exact odds/time and verify relevant settlement terms, including early-payout eligibility where applicable. Distinguish break-even hurdles from genuine forecasts; do not invent probabilities, fair prices or an established edge.

For each shortlisted candidate, give strong source-linked justification: decisive match-level evidence and sample sizes, the tactical mechanism connecting both teams to the selection, the strongest counterargument and how it affected inclusion, and relevant availability/lineup conditions.

Return up to six supported candidates, fewer or none when warranted, and explain what the ordering measures. Give each candidate a clear decision status. Put final selections first and research candidates in a separate table; unresolved material lineup, availability, price or settlement checks prevent final promotion. Include important rejected fixtures and specific reasons. Save the detailed report, coverage inventory (screened, deeply researched and unresolved) and timestamped decision ledger, preserving original statuses and the evidence behind changes. State remaining pre-kickoff checks. Do not force an accumulator or place bets.
```

For Europa or Conference League, replace the domestic-league scope with the relevant competition and date; the same skill includes European competition context.

## Prompt 2 — other markets

```text
Use $football-other-markets and its relevant references for [DATE], Europe/London.

Read AGENTS.md, journal/README.md and journal/active-lessons.md first. Use scripts/journal.py to preserve candidates, important passes, final decisions and later changes; validate after saving.

Screen the men's top divisions in England, Spain, Germany, Italy, France, Netherlands, Portugal, Belgium, Scotland and Türkiye. Verify fixtures, actual venues, kickoffs and status; research that day only and exclude matches already started. Consider match/team goals, handicaps, corners and cards. Exclude BTTS No and keep player combinations in the separate builder workflow. Choose markets for their evidence, not simply to increase the odds.

Use gpt-6.2-astra at high effort as the selected lead (choose it in the model picker; the skill cannot switch it). Keep the lead responsible for analysis and final decisions. Where supported, explicitly use gpt-6-luna at extra-high (`xhigh`) effort for bounded data, team-news, market and rule retrieval, and gpt-6.2-sol at high effort to challenge the finalists. Audit decisive evidence and report the models actually used; disclose unavailable routes.

Apply the full skill methodology: a broader comparable baseline and recent 5–10 relevant games where available, actual sample sizes, opponent/venue context, lineup changes and outliers. Show match-by-match counts, failures and distance from the exact offered threshold; preserve missing data.

Use market-specific evidence: both teams' chance creation/prevention for goals; winning margins and opposing scoring routes for handicaps; corner production/concessions, width, blocked deliveries and game state for corners; contact exposure and comparable referee evidence for cards. Explicitly test whether an early comfortable lead could suppress corners.

Compare each finalist with its most relevant alternative at contemporaneous prices, including a winner or BTTS Yes case when already researched and relevant. Explain which game states support one and defeat the other; a higher price or attractive hit rate alone does not establish superiority. Verify UK bet365 prices where accessible, otherwise identify the alternative source. Record exact odds/time and verify time periods, Asian versus three-way settlement, pushes, quarter-lines and relevant counting rules.

For each candidate, give strong source-linked justification: decisive counts and sample sizes, tactical mechanism, strongest counterargument and its effect on inclusion, lineup conditions and why this particular market is preferred. Return up to five supported candidates, fewer or none when warranted, and explain the ordering. Give each candidate a clear decision status. Put final selections first and research candidates in a separate table; unresolved material lineup, price or contract checks prevent final promotion. Keep same-game alternatives separate and explain dependence.

Include important rejected markets and fixtures with reasons. Save the detailed report, coverage inventory (screened, deeply researched and unresolved) and timestamped decision ledger; preserve original statuses and record evidence behind changes. State remaining pre-kickoff checks. Do not invent probabilities, fair prices or an established edge, force an accumulator or place bets.
```

## Prompt 3 — bet builders

```text
Use $football-bet-builders and its relevant references for [MATCHES OR COMPETITION] on [DATE], Europe/London. Verify each fixture's date, kickoff, actual venue, competition and status; exclude matches already started. Investigate two selections per match, with a third only when separately justified. This is a research target, not a quota: one player watch or no suitable builder is a valid outcome.

Read AGENTS.md, journal/README.md and journal/active-lessons.md first. Respect the project's BTTS Yes-only preference inside builders. Use scripts/journal.py to preserve candidates, important passes, final decisions and later changes; validate after saving.

Check which UK bet365 markets and exact thresholds are actually offered before deepening candidates. Consider player total shots, shots on target, fouls committed, to be fouled and tackles, plus a team market only when its evidence warrants it. Verify the bookmaker's event definitions and that the evidence feed measures the same statistic, especially tackles versus tackles won. Investigate reasonable prices without raising thresholds merely to inflate the payout.

Use gpt-6.2-astra at high effort as the selected lead (choose it in the model picker; the skill cannot switch it). Keep the lead responsible for role/tactical analysis, dependence and final decisions. Where supported, explicitly use gpt-6-luna at extra-high (`xhigh`) effort for bounded player ledgers, current availability and price/rule retrieval, and gpt-6.2-sol at high effort for a focused independent challenge. Audit decisive rows, wait for relevant findings and report the models actually used. Disclose unavailable routes.

Apply the full skill methodology: recent match-level counts with minutes, verified starts/subs, opponents and roles; a broader comparable baseline; current availability, set-piece duties, substitution risk and relevant referee context. Keep actual sample sizes, zeros, missing counts and non-appearances distinct. Separate club and national samples and exclude extra-time events from ordinary 90-minute comparisons. Compare every proposed threshold with the relevant adjacent line, showing hits, misses, missing observations and threshold distance.

Establish a specific role-and-opponent opportunity mechanism for each leg. For tackles, show how controlled opposition possession reaches the player's defensive zone and creates legal ground challenges; historical counts, winger reputation or broad possession expectations alone are insufficient. Exclude a leg when its opportunity case is unsupported.

For each leg, present the decisive ledger evidence with source links, the strongest counterargument and its effect on inclusion, and starting-role conditions. Then explain the pair's dependence, competition for opportunities and shared failure scenarios, including early leads, tactical changes and substitutions. A strong first leg cannot compensate for a weak second leg.

Give exact selections and timestamped individual prices alongside the actual combined bookmaker quote. Mark missing combined quotes pending; never substitute multiplied singles. Verify non-starter, substitution/replacement, extra-time and void rules. An eligible early-payout result leg does not settle other builder conditions.

Give each pair a clear decision status. Put final builders first and exploratory pairs in a separate table; unresolved material starting-role, market, contract or actual combined-price checks prevent final promotion. State when none qualifies. Explain the ranking and important rejected players, thresholds and combinations. Save the detailed report, fixture coverage inventory and timestamped decision ledger, preserving original statuses and the evidence behind changes. State remaining pre-kickoff checks. Do not invent probabilities, fair prices or an established edge, automatically combine every match into an accumulator, or place bets.
```

## Matchday refresh

In the same research chat, send:

```text
Recheck the existing shortlist using confirmed lineups, fresh availability, current odds and the exact settlement terms. Keep the original report for comparison. Explain what changed and label every candidate keep, downgrade, remove or still pending. Do not fill gaps with weaker replacements. Update the decision ledger before kickoff.
Keep unresolved candidates outside the final selection table. For alternative markets on the same game, compare the winner/BTTS case directly with the proposed alternative, including prices, extra failure modes and why one is preferred. If none completes the material checks, return no final selection for that game.
```

Use a new refresh request when the relevant lineups are actually available; one early check cannot verify later team sheets automatically. The refresh is narrower than a new full-slate investigation; keep the chosen routes and focus only on changed evidence.

## What the skills preserve

They retain the useful research principles from earlier analysis: screening broadly, deeply comparing finalists, analyzing both opponents, checking underlying chance production, tactical exposure, current lineups, price and reasons to exclude uncertain games. They add clearer safeguards around sample size, player minutes, market definitions, missing data, correlation and prospective review.

They do not preserve a proven winning formula. Three successful slates are encouraging but too small to establish a sustainable edge, and wins/BTTS results do not validate new player-prop markets. The skills are thorough research procedures; quality still depends on sources, judgment and honest decisions to pass.

## Local journal (no UI)

Every research skill now reads the project journal and archives its decisions. Use `$football-journal` to archive supplied reports, verify named completed slates, or review process lessons. The implementation lives in `journal/README.md`; run `python3 scripts/journal.py validate` and `python3 scripts/journal.py summary` to inspect it. No automatic schedule is enabled.

Example: `Use $football-journal to verify the recorded decisions for [DATE], Europe/London, and review the evidence behind wins and losses. Preserve original statuses, distinguish retrospective discoveries from pre-match evidence, and propose only specific, prospectively testable improvements. Do not make new selections or place bets.`
