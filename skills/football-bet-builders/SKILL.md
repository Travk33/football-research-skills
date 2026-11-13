---
name: football-bet-builders
description: Research two or three compatible football selections per fixture, especially player shots, fouls, fouled and tackles, using exact available markets, minutes, tactical exposure and actual combined prices. Use for bookmaker bet-builder research rather than ordinary match-winner shortlists.
---

# Football bet builders

Construct a small, defensible same-match combination when the evidence and offered terms support one. The user's requested two or three picks per game is a target to investigate, not a reason to fabricate a second leg. Some competitions do not offer fouls or tackles. Verify availability for the exact fixture and bookmaker.

Read [model-routing.md](references/model-routing.md) before assigning retrieval work. Use cheaper workers for bounded ledgers and rule extraction; retain a stronger reasoning lead for tactical interactions, threshold decisions, source conflicts and the final pair. Read [player-markets.md](references/player-markets.md) for market-specific checks and [evidence-contract.md](references/evidence-contract.md) for extraction, handoff and report formats.

## Frame the fixture and contract

Verify date/timezone, kickoff, competition, actual venue and fixture status. State whether the analysis is pre-match or in-play. Check current squad withdrawals, suspensions, registration and matchday news. A listed player or predicted XI is not a confirmed starter.

Inspect the named bookmaker's available markets and exact thresholds before deepening candidates. Record bookmaker/region, quote time, single price and exact label. Distinguish total shots from SOT, fouls committed from fouled, and tackles from tackles won. An empty player row does not establish an available line or price.

Verify non-starter, substitution/replacement, extra-time and void rules relevant to the contract. Do not infer terms from a promotion badge. Early payout for an eligible result leg does not settle the other builder legs. Research can prepare a price comparison; it does not authorize a betting transaction.

## Build a player ledger

For each plausible player, collect recent match-level counts, minutes, starter/sub status, role, opponent, competition and source, plus a broader comparable baseline when available. Keep zeros, missing fields, DNPs and substitutions distinct. Confirm fixture identity after scraping historical links; URL fragments may be lost.

Use a national-team sample for international roles and club evidence as separate corroboration. Do not pool them into an unexplained last-ten percentage. Five appearances including two 15-minute substitutions are not five comparable starts. Per-90 averages alone can conceal minutes risk and event clustering.

Evaluate the exact offered line and the immediately relevant alternative. Report how often each was met, failures, sample size and threshold distance. A player who has one foul in four games may have poor evidence for two. Do not raise a threshold just because the safer line is short.

Confirm whether the player's role plausibly persists: set pieces, penalty duty, central versus wide position, pressing assignment, defensive cover and realistic substitution pattern. Starting does not guarantee 90 minutes. Use current team news and distinguish fact from projection.

## Test the mechanism against the opponent

For shots, connect player shooting involvement to team creation and opponent concessions; for SOT additionally assess accuracy and shot type. For fouls, connect defensive exposure to the opponent's dribbles, movement and the referee's recorded events. For fouled, connect receiving/carrying volume to actual contact. For tackles, connect opponent controlled-possession attacks to legal ground challenges. A high duel-win percentage is not a tackle-count forecast.

Describe the likely zone or role interaction and the evidence behind it. Do not invent a guaranteed full-back/winger marking assignment. Note cover defenders, formation switches and situations where the player can avoid the event. Referee averages from unrelated competitions are weak context, not a numeric adjustment.

Before promoting a tackle leg, establish an opportunity case as well as a count history: how will this opponent bring controlled possession into the player's defensive zone, and why should enough ground challenges occur at the offered threshold? If that mechanism is unsupported or contradicted by the likely game state, exclude the leg from the actionable combination. A caveat beside an attractive historical hit rate is not a substitute for this decision. Do not infer opportunity from the opposing winger's reputation alone; use the tackle-specific checks in `player-markets.md`.

Use team xG, possession and game-state expectations as context rather than a substitute for player events. Missing teammates can redistribute attempts but also weaken team creation. A favorite winning easily can reduce late shooting or defensive activity. Retain the strongest opposing scenario.

## Combine only after assessing each leg

Explain why both events can occur and what shared state can defeat them. Two attackers can benefit from team chances while competing for shots; a midfielder and defender can both rely on opponent possession; a foul-drawn and foul-committed leg can share an incident. Different players do not establish independence.

Do not multiply same-game singles and label the result an offered builder price. Obtain the **actual joint quote** through permitted read-only/preparatory means or from the user's current slip. If unavailable, give individual prices and mark the combination **quote pending**. Never invent a bookmaker price or transaction.

Treat any four-match builder accumulator as all its required conditions, e.g. two picks from four games means eight events. Across-match independence is an approximation, not a certainty; model and information errors can be shared. Do not encourage additional legs solely to reach a target payout.

## Price and confidence

`1/decimal_odds` is an ordinary binary price hurdle, not the forecast. Descriptive hit rates in small samples are not reliable event probabilities. Do not claim a fair price or positive expected value without an explicit forecasting method, uncertainty and relevant validation.

If a count model is appropriate, account for minutes, role, opponent exposure, clustering/overdispersion and substitution mixture. Label Poisson or other simplified calculations as illustrations when unvalidated. Do not multiply independently modeled player probabilities without addressing the joint mechanism. Model precision should reflect the evidence rather than the calculator's decimals.

Compare better-supported lower thresholds with genuinely riskier alternatives. If the quote is unattractive, retain the price pass; do not disguise the same weakness by changing the label to “strong builder.” A request for decent odds does not establish a numerical minimum; ask only if that preference materially changes the research.

## Final challenge and deliverable

Before selecting, test each decisive assumption: is the stat exact, are zeros handled correctly, is the sample comparable, does the player start in the expected role, is the tactical interaction plausible, is the line really offered, and does the price refer to this combination? Resolve contradictions or downgrade the candidate.

Return two or three selections only where warranted, with: exact names/lines; individual and actual combined odds clearly separated; evidence counts and minutes; club-versus-country distinction; tactical rationale labeled as inference; strongest counterargument; starting-XI condition; source links; and a status. Use **conditional candidate**, **quote pending**, **reserve**, **price pass**, or **insufficient evidence** as appropriate. Do not call every investigated game a recommended builder.

**Price pass** means evidence does not justify the actual offered terms; without a calibrated joint forecast it does not prove negative expected value. **Insufficient evidence** means one or more event cases cannot be established. **Quote pending** preserves the distinction between a plausible pair and a price-checked selection.

Keep a timestamped pre-match ledger with original statuses and quoted terms. Review later settlements separately from normal event counts, especially replacements and voids. Improve using repeated documented failure mechanisms and prospective checks. Previous win/BTTS successes do not validate a new player-prop model, and a winning builder does not prove the estimated price edge was correct.

During a review, distinguish a failed event from a failed selection process. A foreseeable exposure problem that was noted but did not affect inclusion is a process issue even if other legs won. Preserve watchlist/pass status and record any actual ticket separately; do not retrospectively promote winning reserves or erase losing exploratory legs.
