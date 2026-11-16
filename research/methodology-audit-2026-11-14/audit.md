# Audit of the 5, 7 and 8 November research

Audited 14 November 2026, Europe/London. This reviews saved research and freshly checked public results. Pre-match statistics below are attributed to the saved reports, not reconstructed from today's rolling form tables. Those reports include later clarifications and are not a complete immutable history of every message, final lineup check or accepted wager.

## What the record establishes

| Date | Original coverage | Main group of discussed directions | Public outcome |
|---|---:|---|---|
| Thursday 5 November | 35 fixtures: 17 Europa, 18 Conference | Five wins and two BTTS Yes directions | All seven occurred at full time |
| Saturday 7 November | 37 fixtures across ten top divisions | Four wins and two BTTS Yes directions | All six occurred at full time |
| Sunday 8 November | 44 fixtures across the same ten divisions | User intended five excluding Brighton: four wins and Utrecht–NEC BTTS Yes | All five occurred; omitted Brighton also won |

This supports three successful groups of football directions. It does not verify actual tickets, stakes, accepted odds, promotion eligibility, settlement or profit. No two-goal early-payout rescue is needed to explain these full-time outcomes. Thursday's report explicitly did not certify value or recommend an accumulator; Sunday included reserves and an explicit price pass.

The broader archived subset contains 20 directions: the 18 above, omitted Brighton, and Thursday's explicit Monaco–Nordsjælland BTTS watch. Monaco won 2–0, so that watch failed. Retaining it prevents a winners-only archive. These 20 entries are not all 116 screened fixtures and are not a uniform cohort of final selections.

Scores and sources: [results.json](results.json), [Saturday verification](saturday-worker.md), [Thursday/Sunday verification](thursday-sunday-results.md). Thursday is corroborated by [UEFA](https://www.uefa.com/uefaeuropaleague/news/02ab-22004d716327-dd7c42bc0d91-1000--europa-league-matchday-4-round-up-ferencvaros-triumphant-/) and [BBC Conference results](https://www.bbc.com/sport/football/live/c574pyzklg2zt).

## What was useful in the original method

**Both teams were compared.** Roma's archived season xG was 2.26 for/1.28 against per game versus Sassuolo's 1.33/1.78. The last-five comparison was 1.91/1.56 versus 0.94/2.15. Roma averaged 6.3 SOT, while Sassuolo conceded 6.6. These supported an attacking advantage, but Sassuolo had scored in four of five away games. The report supported the simple win without assuming a clean sheet. Overlapping statistics describe the same performances, not independent probability multipliers.

**Results were tested for distortion.** Thursday's Bournemouth review identified penalties and an early opposition dismissal in the Milan match, conflicting xG providers for the Villa game, and a less extreme broader league baseline of roughly 1.8 xG for/1.1 against. Lugano had eight European goals from 4.03 xG across two matches; rotation and fatigue weakened large-margin arguments. Removing Lech's 5.22 xGA Leverkusen outlier reduced its five-game xGA average from 2.52 to 1.85. Those counterexamples constrained the conclusions.

**BTTS needed two attacks.** ADO and Sparta had recent five-game xG totals of 6.77–10.72 and 10.07–8.83 respectively. That was a bilateral creation/concession case. However, the illustrative independent-Poisson estimate fell from about 69% to 61% if both assumed goal rates fell by 0.25. At 1.50 the hurdle was 66.7%. The sensitivity remains a weakness despite success; this was an uncalibrated illustration.

**Tactics connected numbers to the fixture.** Sunday's Hoffenheim review compared its eight-game 15.16–10.44 xG baseline with Schalke's 7.69–16.60, then used pressing and recovery evidence to explain a possible advantage. It did not assume automatic duel superiority. Benfica's preview discussed Estrela's press/back-five block and Benfica's build-up with three and advancing fullbacks. Celtic's notes identified a flank distinction that contradicted a generic claim about its left wing dominating. These were conditional interpretations, not measured one-on-one probabilities.

**Exclusions mattered.** Saturday left Manchester City out because Forest's weak actual scoring concealed stronger underlying performances, resisted automatically including very short-priced PSG, and questioned Stuttgart–Werder's BTTS price despite strong scoring records. Thursday's Monaco BTTS watch remained below the leading pair because attacking evidence conflicted. Some excluded directions won and some lost; these examples cannot establish that filtering adds value without prospective comparison.

Original report snapshots are in [source-reports](source-reports), with import hashes in [source-manifest.json](source-manifest.json). These identify today's imported files, not authenticated pre-kickoff versions.

## What the wins cannot explain

The results are consistent with useful research, selecting many favourites, and favourable match events. Three slates cannot identify the contribution of each or establish a repeatable advantage over the prices.

- Bayern's 2–1 win came with 3.25–0.82 official xG. Bayern led 2–0 after 57 minutes; Mainz scored at 90+3. A root progress update initially misattributed the late goal to Bayern and was corrected after reading the report. [Bundesliga](https://www.bundesliga.com/en/bundesliga/news/mainz-bayern-munich-match-report-highlights-matchday-9-39922).
- Hoffenheim won 2–1 with 2.28–2.81 xG, an opposition goalkeeper error and substantial Schalke pressure. The result does not confirm complete control; full-match xG also reflects the subsequent game state. [Bundesliga](https://www.bundesliga.com/en/bundesliga/news/hoffenheim-schalke-match-report-highlights-matchday-9-39951).
- Gent needed a late penalty save; Benfica needed a 90+4 winner. These matter for process review without making every narrow win a poor forecast. [Gent](https://www.kaagent.be/nl/team/games/jupiler-pro-league-2026-2027/11/kaa-gent/kv-kortrijk/verslag), [Benfica chronology](https://vsports.pt/vsports/jogo/i-liga/estrela-amadora-benfica/30448/destaques).
- Bournemouth's comeback followed an opposition dismissal. Celtic–Beşiktaş had no SOT at half-time before both attacks eventually scored. [UEFA](https://www.uefa.com/uefaeuropaleague/news/02ab-22004d716327-dd7c42bc0d91-1000--europa-league-matchday-4-round-up-ferencvaros-triumphant-/).
- Utrecht–NEC remained a price pass at 4/9. Its 2–3 result cannot retrospectively turn it into an approved value bet. Brighton remains an omitted reserve despite winning.

The archive lacks a complete prospective final-selection ledger, verified closing prices and calibrated forecasts. We cannot quantify a model edge or causally attribute the wins to extra tactics, xG, a model tier or a skill. A winning streak must not set the confidence level for a new slate or transfer to corners/player props.

## Skill audit and changes

The installed winner/BTTS skill retains season and recent comparable samples, both-team ledgers, opponent and venue context, consistent xG providers, chance quality, incidents, availability, roles, rest/travel, tactics, exact prices, counterarguments and original-status preservation. Other-markets/builders retain their distinct threshold, opportunity, minutes and settlement tests. See [independent audit](skill-review.md).

This new AI-Bets clone lacked the installed November 13 safeguards. Its three skill entrypoints, usage guidance and validation cases have been brought forward from the older working repository. The user's BTTS Yes-only preference is in [AGENTS.md](../../AGENTS.md), including builders; it is not a universal claim about market quality.

Two narrow additions to the winner/BTTS skill were synced to its installed copy:

1. Reproducible screening with separate market dispositions, sources, unknowns, reopening criteria, review of close exclusions/weak coverage, and honest coverage counts.
2. Explicit checks of result period and relevant void/postponement terms.

These improve traceability and execution; they do not establish better forecasting accuracy. No fixed metric weights, arbitrary probabilities or selection quotas were introduced.

## A typical 44-game Saturday

1. **Verify the inventory.** Account for every fixture in the requested date and Europe/London timezone across men's top divisions in England, Spain, Germany, Italy, France, Netherlands, Portugal, Belgium, Scotland and Türkiye. Record actual venue, kickoff and status.
2. **Screen every fixture consistently.** Compare both teams' broad strength, recent comparable chance/scoring evidence, venue, material news, available price and data quality. Give winner and BTTS Yes separate dispositions. A balanced match can fail the winner screen while retaining a plausible BTTS case. Missing xG is unknown, not evidence of a weak attack.
3. **Deepen plausible and borderline cases.** An illustrative workload could be 44 screened, 12 deeply researched, five remaining candidates and three completed selections. These are not targets. Retrieve recent five-to-ten comparable match rows and broader baselines for both teams, preserving incidents, sources, denominator and failures. Investigate decision-changing uncertainty rather than accumulating loosely relevant metrics.
4. **Test the mechanism and failure scenario.** Winners need a superiority case, opponent scoring routes and draw risk. BTTS Yes needs a separate credible scoring route for each attack against this defence. Study press/build-up, transition space, wide combinations/cover, aerial/set-piece exposure and expected roles. Duel attempts and success rates matter only for relevant zones and comparable roles; a duel percentage alone cannot forecast goals or tackles. Treat exact winger/fullback assignments as conditional. Test an early lead and a different XI.
5. **Challenge finalists and close exclusions.** Give an independent reviewer the task and evidence without requiring endorsement. Verify decisive rows, test removing the most flattering outlier, inspect opposition responses and reopen plausible exclusions. This limits selection bias without pretending all 44 received identical depth.
6. **Decide at actual terms.** Compare already-researched alternatives for a fixture at comparable depth and contemporaneous quotes. A slightly higher payout cannot justify a weaker event. Explain what the ordering measures: evidence robustness, estimated likelihood and price assessment are different. Reciprocal odds are a hurdle, not a forecast. Numerical value claims need a declared, validated model. Fewer selections or none are valid.
7. **Clear material conditions before final status.** Check fresh odds, contract and the XI/availability conditions the case actually depends on. Keep unresolved rows conditional; record promotion/downgrade time and new evidence. Early reports do not refresh themselves. Do not join category watchlists just to fill an accumulator.
8. **Review the entire recorded cohort.** Save selections, reserves, passes and known gaps before kickoff. Append results and changes without rewriting the original call. Separate FT outcomes, game-state context, actual eligible promotional settlements and process lessons. Compare same-contract closing prices where recorded; assess calibration only for genuine pre-recorded forecasts. Test changes on future slates.

## Execution and validation scope

GPT-6 Luna at medium effort handled bounded extraction/results and two fictional behavior checks. GPT-6.1 Sol at high effort independently reviewed the skills. The lead read the reports, checked decisive sources, reconciled findings and made changes.

The fictional checks separated the win and BTTS screens, retained missing evidence, challenged weak coverage and preserved historical statuses. Packaging validation is recorded in [validation.txt](validation.txt). These check behavior/file integrity, not betting accuracy. The original journal design inventory remains unchanged as its historical handoff; this audit adds a dated record. No journal application, scheduled verifier, new shortlist or wager was created.

