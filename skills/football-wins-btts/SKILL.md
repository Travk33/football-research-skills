---
name: football-wins-btts
description: Research football match winners and both-teams-to-score selections using current team evidence, availability and prices. Use for domestic leagues, European cups and internationals; route player builders or other market families to their own workflows.
---

# Football wins and BTTS

Produce a source-linked shortlist with strong reasons both for and against each candidate. Preserve the user's date, competitions, exclusions and requested market scope. Do not equate a desired number of legs with that many worthwhile selections.

## Route work intelligently

Read [model-routing.md](references/model-routing.md) when selecting a lead or delegating. Prefer a capable reasoning lead for comparative judgment and a cheaper model for bounded retrieval and extraction. Delegate independent competition or team ledgers when useful; the lead must reconcile them and review decisive evidence. A worker's confident wording is not verification.

For competition-specific context, read [competition-context.md](references/competition-context.md). For a post-match audit or method change, read [review-and-improvement.md](references/review-and-improvement.md). These references supplement the workflow; do not load unrelated sections merely to increase apparent thoroughness.

## Establish the slate

- Resolve the actual date and timezone, home/away venue, competition stage, kickoff and status from current sources. Use official competition schedules where available. Exclude started or postponed games from a pre-match shortlist unless explicitly requested otherwise.
- Keep an inventory of all screened fixtures and distinguish basic screening from deep analysis. “Second candidate investigated” must not become “second most likely among 44 matches.” Define what any ranking measures.
- Screen for data coverage, meaningful team-strength differences, availability uncertainty and prices. Deepen the plausible cases and retain concise rejection reasons; do not exhaustively collect every metric for every fixture.

## Build comparable evidence for both teams

Use a broader current-season or comparable baseline alongside recent five-to-ten-match form where available. Retain the actual denominator if fewer comparable matches exist. Home/away splits, competitive context and opponent strength matter more than selecting whichever window looks strongest.

Keep a compact match ledger: date, opponent, venue, competition, score, xG/xGA provider, shots/SOT for and against, penalties, red-card timing, important lineup context and source. Missing values are unknown, not zero. “Last five matches with xG” is not necessarily the last five matches played. Verify fixture identity and date when retrieving historical match pages; some scrapers drop URL fragments and return another fixture.

For attacking and defensive strength, prioritize chance quality and volume: non-penalty xG when actually available, box entries/shots, SOT, big chances, set-piece exposure and repeatability. Compare actual goals with underlying chance production to flag finishing/goalkeeping variation. Do not mechanically stack correlated metrics as independent votes.

Use one xG provider within a numerical comparison. If providers disagree, retain the disagreement and show the decision's sensitivity. Multiple websites sharing one feed are not independent corroboration. Do not claim opponent adjustment or 11-v-11 adjustment unless it was actually calculated; qualitative context should be labeled qualitative.

Identify early dismissals, penalties, own goals, heavily rotated cup games and extreme scorelines. Show the full sample and, if useful, a transparent sensitivity excluding a specified distortion. Do not discard unfavorable matches while keeping favorable outliers.

## Connect evidence to the exact market

**Winner:** assess both the favorite's chance creation and ability to suppress the opponent. Explain the opponent's realistic scoring routes and draw risk. A strong attack can support a win without supporting a clean sheet or large handicap. A losing opponent with competitive xG is different from an opponent consistently outplayed.

**BTTS:** establish a credible scoring route for each team separately. Evaluate attack versus opposing defense, venue, transition and set-piece routes, goalkeeper/defensive absences and the possibility one side creates little. A high match-goal total can be driven entirely by one team. Weak defenses alone do not prove both attacks will score.

For tactics, name a plausible mechanism and its evidence: press versus build-up, wide overloads and defensive cover, space behind an advancing full-back, aerial/set-piece mismatch or transition exposure. Treat uncertain matchups as conditional. Head-to-head is secondary when managers, roles, squads or venues differ. Duel-win percentage alone does not establish territorial control or scoring probability.

Check official availability, suspension/registration, likely XI, rest/travel and schedule incentives. Distinguish confirmed absent, doubt, available, projected starter and confirmed starter. State the lineup change that would remove or downgrade the candidate. Recheck decisive news near kickoff when the task allows it.

## Price without false precision

- Record bookmaker, region, exact market and line, decimal odds, observation time and source. Distinguish direct quotes from comparison sites and user screenshots.
- For an ordinary binary bet, `1 / decimal odds` is the break-even price hurdle, not the model forecast or a margin-free probability. Do not label this column “our probability.” Removing margin requires all mutually exclusive prices from the same market/time and still produces a market reference.
- Separate descriptive evidence, any model estimate and the price verdict. Without a declared numerical forecasting method, say whether the direction is supported and whether value remains unestablished; do not invent fair odds or a minimum acceptable price.
- If modeling, declare the training/calibration basis, opponent/venue treatment, parameter uncertainty and key assumptions. A simple Poisson illustration is not a calibrated forecast. Stress-test plausible rates and lineup scenarios; do not use precise percentages to conceal sparse data.
- For push-capable markets use `EV = P(win)*(odds-1) - P(loss)` and account for refund outcomes. Do not apply binary reciprocal odds to unconditional win probability. For accumulators, distinguish individual from joint probabilities and explain dependence rather than automatically multiply.
- Verify early-payout eligibility. A two-goal lead can settle an eligible result leg; it does not settle unrelated BTTS/corner/player legs. Record normal result and promotional settlement separately.

## Decide and deliver

Before deciding, challenge each candidate: what evidence would favor the opponent or a no-bet decision, what depends on an unconfirmed assumption, and would the case survive removal of its most favorable match? Resolve contradictions or explicitly lower confidence.

Use clear statuses: **conditional candidate** (XI/quote still needed), **selection at observed terms** (all stated gates satisfied), **reserve**, **price pass**, **insufficient evidence**. Being the best available candidate does not imply high absolute confidence or positive expected value.

A **price pass** means the available evidence does not justify accepting the offered terms; without a calibrated forecast it is not proof of negative expected value. **Insufficient evidence** means the football/statistical case itself cannot be established. Use **quote pending** when the required price is absent instead of declaring a price pass from an invented quote.

Deliver a concise comparison table with exact selection, kickoff, observed odds/time, status and principal reason. Follow with evidence counts, strongest counterargument, tactical inference, lineup condition and source links for each finalist. Explain important rejected candidates. Report evidence confidence separately from estimated event probability; omit a numerical probability if none was defensibly modeled.

Record a timestamped decision before kickoff, including passes and reserves. Retain the original status, price, evidence and any pre-recorded numerical forecast. Improve through the review reference; a small winning streak is not proof of an edge, and a close winner does not alone justify rewriting the method.
