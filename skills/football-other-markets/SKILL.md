---
name: football-other-markets
description: Research football goal totals, team totals, handicaps, corners and cards using market-specific evidence, current availability and settlement rules. Use when comparing alternatives to straight wins or BTTS; player combinations belong in the bet-builder workflow.
---

# Football other markets

Choose a market because the evidence supports its event mechanism, not because a short winner price needs padding. Preserve the requested slate and exclusions. Return fewer selections when coverage or prices are inadequate.

Read [model-routing.md](references/model-routing.md) for efficient lead/subagent choices. Cheaper workers can retrieve source-linked ledgers and terms; the reasoning lead compares market families, reconciles conflicts and decides. Read [market-mechanics.md](references/market-mechanics.md) only for the market families under consideration.

Read [journal-workflow.md](references/journal-workflow.md) at the start of every run and save decisions/reviews to the active project journal. Read [decision-quality.md](references/decision-quality.md) when assessing finalists, missing chance-quality evidence or whether a pending check can actually resolve the case. Publish completed selections before research-only candidates.

For efficient shared collection and bounded model execution, read [pipeline-workflow.md](references/pipeline-workflow.md) when the active project provides the scoped pipeline. Keep tactical judgment with the selected lead.

## Establish reliable inputs

Verify current date/timezone, kickoff, venue, competition stage and fixture status. Inventory the screened matches and distinguish deep research from initial screening. Verify whether the bookmaker actually offers the exact market.

Collect a broader comparable baseline plus recent five-to-ten matches when available, with a relevant home/away split. Record actual sample size, dates, opponents, minutes/game state, provider and source. Keep domestic, continental and international settings distinct. Treat opponent strength quantitatively only when adjustment was really calculated; otherwise label it qualitative.

Retain game-by-game counts, not just averages. Two samples with the same mean can have very different probabilities of crossing a line. Show failures and distance from the threshold. Four corner totals all equal to six provide a different margin of error from four totals above ten.

Missing data are unknown, not zero. Confirm the exact historical fixture when a scraped URL contains a fragment. Preserve xG-provider consistency. Red cards, penalties, extra time, extreme opponents and rotation can distort recent records; retain the original sample and any explicitly defined sensitivity check. Do not count related metrics or multiple copies of the same data feed as independent evidence.

## Match the metric to the market

- **Goals and team totals:** combine both teams' chance creation/prevention, non-penalty xG if available, shot quality, finishing variation, goalkeeper/attacking absences and likely game states. Test tails around the exact line; an average alone cannot establish under/over probability.
- **Handicaps:** analyze winning-margin distribution and the opponent's scoring route. A likely winner does not automatically cover a large handicap. Verify Asian versus three-way settlement and which team receives the handicap.
- **Corners:** examine own corners and opponent concessions, territorial play, width, crossing/blocked deliveries, shot blocks and lead/trailing states. Possession alone is insufficient. Goal efficiency can reduce subsequent pressure and corners.
- **Cards:** combine comparable referee behavior, team/player contact exposure, stakes and actual market definitions. Fouls and cards are different events. Do not import a domestic referee average as an international forecast without explaining the mismatch.

Use current official availability and disciplinary information. Distinguish projected from confirmed XI and explain how changed players alter the market mechanism. A missing winger may affect corners differently from match goals. Confirm qualification/aggregate incentives; “must win” is context, not a numerical scoring uplift.

State tactical inferences as mechanisms with observable support: which side creates the exposure, which player/unit responds and what could break the mechanism. Do not invent exact marking assignments or arbitrary percentage uplifts.

## Contract and price first

Record bookmaker/region, exact market name, line, time period, odds, quote timestamp and rule source. Verify whether extra time counts, how postponement/abandonment works where relevant, and what equality means on an integer line. “Over 5 corners” in a three-way market is not an Asian over 5 contract.

For ordinary binary settlement, `1/decimal_odds` is the break-even hurdle, not an estimated probability. For a push-capable single, use `EV = P(win)*(odds-1) - P(loss)`; reciprocal odds refers to the win share among resolved outcomes, not unconditional win probability. Split quarter-lines into their two half-stake components. Do not invent an EV calculation without defensible probabilities.

Separate observed hit rates, illustrative model outputs, calibrated forecasts and price judgments. If a model is used, identify the data basis, distribution assumptions, uncertainty and validation. Poisson goal assumptions are not automatically suitable for corners, cards or heavily overdispersed player events. No fair odds or price floor should be invented to make a qualitative opinion look numerical.

Different same-match markets may share one game-state assumption. Treat them as alternatives unless the request explicitly concerns a combination; then evaluate dependence and obtain the actual builder quote. Do not multiply same-game singles as if that verifies an offered price.

## Decision and report

For each finalist, compare at least the most relevant competing interpretation: e.g. team total versus match total, corners versus goals, or a lower versus higher line. Explain why the chosen contract best expresses the evidence. State the strongest counterargument and the lineup/price condition that would remove or downgrade the candidate. Some counterarguments remain unresolved even after lineups are confirmed.

When an alternative is preferred to a researched match winner or BTTS event, compare them directly at contemporaneous prices. Show which shared game states support one but defeat the other: an early efficient lead can help a winner while suppressing corners. State why the preferred event clears the inclusion standard despite its strongest observed counterexample and relevant venue split. A small price improvement, pooled hit rate or lower reciprocal hurdle does not establish superiority. If the comparison remains unresolved, retain research status rather than call the alternative the best selection.

Use **conditional candidate**, **selection at observed terms**, **reserve**, **price pass**, or **insufficient evidence**. Do not fill an accumulator to meet a target return. “Most supported of these” is not a probability ranking.

**Price pass** means the evidence does not justify the offered terms, not proven negative expected value without a calibrated forecast. **Insufficient evidence** means the event case cannot be established. When the actual quote is missing, use **quote pending**, not an invented price judgment.

Separate research candidates from final selections. Do not place a candidate in a main/final ticket table while a declared material XI, price or contract condition remains unresolved. Answer requests to confirm a “main bet” from those conditions, not from the presence of a row in a watchlist. Record the time, new evidence and reason for any promotion or downgrade. A broader search or requested leg count does not lower the inclusion standard.

Provide a table of selection, kickoff, exact odds/time and status, followed by recent counts, baseline/context, tactical explanation, limitations and direct source links. Give decisive evidence rather than a long list of loosely relevant statistics. Report verified terms separately from unresolved terms.

Timestamp the pre-match decision, including rejected alternatives. In review, retain its original status and distinguish actual statistical outcome from promotional/void settlement. Track comparable prices and forecasts prospectively; do not infer a proven edge from a short winning streak or transfer a win/BTTS record to these different markets.
