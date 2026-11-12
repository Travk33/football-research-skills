# Using the three football research skills

## Choose the lead in Codex

For demanding routine research, use **GPT-6 Astra / Extra High** with the explicit delegation instructions below. For a large Saturday slate where usage is less important, **Astra / Ultra** is a reasonable option if available. Ultra enables proactive delegation and maximum reasoning; it is not required to use subagents. For a lower-cost lead, use **GPT-6.1 Sol / High** and keep the same prompts. These are workflow recommendations, not validated differences in football prediction performance. [Official model guidance](https://learn.chatgpt.com/docs/models).

Select the model and effort under the composer before sending the prompt. If a supported Ultra option is hidden, official guidance points to Settings > Configuration > Ultra in model picker slider; availability depends on the account/client. No settings are changed by these documents.

Explicitly name cheaper workers. Without model/effort overrides or configured defaults, subagents can inherit the lead's model and effort. The prompts request Luna for retrieval and Sol for review, with the selected lead responsible for judgments. A skill does not switch the lead or enforce a guaranteed router. [Official subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Start a request

1. Open a new Codex chat, preferably in the football research project so earlier reports are available when you ask for comparisons.
2. Choose the lead model and reasoning effort.
3. Replace `[DATE]` with a calendar date and any bracketed fixture field with your intended scope. Keep Europe/London if you want UK kickoffs. This avoids ambiguous “next Saturday” dates during international breaks.
4. Paste one prompt below. The installed skill is invoked with `$skill-name`. If it is not found, ask the agent to check its installed skill folder rather than claim it used it. [Skill invocation](https://learn.chatgpt.com/docs/changelog).
5. Review the shortlist, then request a fresh XI/price check when lineups are published. An early report remains conditional until its stated gates are satisfied.

## Prompt 1 — winners and BTTS

```text
Use $football-wins-btts and its relevant references for matches on [DATE], Europe/London.

Screen the men's top divisions in England, Spain, Germany, Italy, France, Netherlands, Portugal, Belgium, Scotland and Türkiye. Verify that the matches actually take place on this date. Research that day only.

Keep the selected lead model responsible for methodology, tactical interpretation, conflicting evidence and final decisions. Where supported, explicitly use gpt-6-luna at medium effort for independent fixture/statistics/team-news retrieval and gpt-6.1-sol at high effort for a focused challenge of the final shortlist. Give workers bounded tasks, audit decisive evidence and report the models actually used. If those routes are unavailable, continue with available tools and state the limitation.

Compare both teams using a season baseline and recent 5–10 comparable games where available, home/away context, opponent quality, xG, shots/SOT, availability, rest, tactics and distortions from red cards or penalties. Establish a scoring route for each side in BTTS cases. Check current UK bet365 prices where accessible, otherwise clearly identify another source.

Return up to six strongest supported win/BTTS candidates, fewer if warranted. For each give source-linked evidence, the strongest counterargument, exact odds/time, lineup conditions and a clear decision status. Distinguish break-even hurdles from genuine forecasts. Include important rejected games, explain the shortlist order, and save a detailed report plus timestamped decision ledger. Do not force an accumulator or place bets.
```

For Europa or Conference League, replace the domestic-league scope with the relevant competition and date; the same skill includes European competition context.

## Prompt 2 — other markets

```text
Use $football-other-markets and its relevant references for [DATE], Europe/London.

Screen the men's top divisions in England, Spain, Germany, Italy, France, Netherlands, Portugal, Belgium, Scotland and Türkiye. Consider match/team goals, handicaps, corners and cards. Choose the market that best matches the evidence for each fixture; do not add markets simply to increase the odds.

Keep the selected lead model responsible for analysis and final decisions. Where supported, explicitly use gpt-6-luna at medium effort for bounded data, team-news, market and rule retrieval, and gpt-6.1-sol at high effort to challenge the finalists. Audit decisive evidence and report the models actually used; disclose unavailable routes.

Apply the full skill methodology: broader baseline plus recent comparable match counts, opponent and venue context, tactical mechanisms, lineup changes, outliers and the exact offered threshold. Verify UK bet365 prices where accessible and the actual settlement terms, including Asian versus three-way lines, pushes and time periods. Explain the best relevant alternative market or line for each finalist.

Return up to five supported candidates, fewer if warranted, with source-linked evidence, exact odds/time, strongest counterargument, lineup/price conditions and clear status. Keep same-game alternatives separate and explain dependence. Do not invent probabilities, fair prices or missing data. Include passes and save a detailed report plus timestamped decision ledger. Do not place bets.
```

## Prompt 3 — bet builders

```text
Use $football-bet-builders and its relevant references for [MATCHES OR COMPETITION] on [DATE], Europe/London. Research two selections per match, with a third only when separately justified.

Check which UK bet365 markets are actually offered. Consider player total shots, shots on target, fouls committed, to be fouled and tackles, plus a team market only when it improves the evidence-based case. Investigate reasonable prices without raising thresholds merely to inflate the payout.

Keep the selected lead model responsible for role/tactical analysis, dependence and final decisions. Where supported, explicitly use gpt-6-luna at medium effort for bounded player ledgers, current availability and price/rule retrieval, and gpt-6.1-sol at high effort for a focused independent challenge. Audit decisive rows, wait for relevant findings and report the models actually used. Disclose unavailable routes.

Apply the full skill methodology: recent game-by-game counts with minutes and verified starts/subs, a broader comparable baseline, expected role and substitutions, opponent exposure, relevant referee context, and exact market definitions. Keep club and national samples separate. Compare the proposed threshold with the next relevant line and retain failed observations.

For each supported pair, provide exact selections, source-linked counts, tactical rationale, strongest counterargument, lineup conditions, individual prices and the actual joint quote. Mark unavailable quotes as pending; never present multiplied singles as a verified builder price. Rank pairs by explained evidence strength and retain weaker games as passes. Do not automatically combine all matches. Save the report and decision ledger; do not place bets.
```

## Matchday refresh

In the same research chat, send:

```text
Recheck the existing shortlist using confirmed lineups, fresh availability, current odds and the exact settlement terms. Keep the original report for comparison. Explain what changed and label every candidate keep, downgrade, remove or still pending. Do not fill gaps with weaker replacements. Update the decision ledger before kickoff.
```

Use a new refresh request when the relevant lineups are actually available; one early check cannot verify later team sheets automatically. The refresh is narrower than a new full-slate investigation and normally does not need Ultra.

## What the skills preserve

They retain the useful research principles from earlier analysis: screening broadly, deeply comparing finalists, analyzing both opponents, checking underlying chance production, tactical exposure, current lineups, price and reasons to exclude uncertain games. They add clearer safeguards around sample size, player minutes, market definitions, missing data, correlation and prospective review.

They do not preserve a proven winning formula. Three successful slates are encouraging but too small to establish a sustainable edge, and wins/BTTS results do not validate new player-prop markets. The skills are thorough research procedures; quality still depends on sources, judgment and honest decisions to pass.
