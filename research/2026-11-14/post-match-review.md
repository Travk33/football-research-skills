# Nations League review: 14 November 2026

Review assembled 15 November 2026, Europe/London, using the original 03:45:11 GMT decision record and separately dated post-match verification. The original report, coverage inventory and decision ledger have not been rewritten. This is a retrospective review, not a new prediction or a claim of actual betting settlement.

## Recorded decisions and results

The original slate had **two retained research directions and zero final selections**. That prevents misreporting an approved ticket, but does not exempt the quality of the candidates or their presentation from review.

| Original direction | Original status / price | FT result | Direction outcome |
|---|---|---|---|
| Portugal win | Conditional candidate, 1.50 | Portugal 1–4 Denmark | Lost |
| Sweden win | Reserve, 1.50 | Sweden 3–2 Bosnia and Herzegovina | Won; remains a reserve |
| Portugal–Denmark BTTS Yes | Price pass, 4/7 = 1.5714 | Both scored | Would win; remains a pass |

Other screened results: Kosovo 0–0 Israel; Norway 3–1 Wales; Georgia 0–2 Hungary; Northern Ireland 1–0 Ukraine; Austria 1–0 Republic of Ireland; Romania 2–1 Poland. The journal preserves the screened win and BTTS Yes directions, including winning exclusions. It does not turn them into recommendations after the fact.

Sources: [original report](report.md), [original ledger](decision-ledger.json), [coverage](coverage-inventory.json), [result verification](post-match-results.json), [FotMob day feed](https://www.fotmob.com/api/data/matches?date=20261114).

## Portugal: the concern was partly right, but needs separating by match

The original research correctly identified injuries/suspensions affecting Portugal's width and full-back cover, Denmark's Damsgaard–Højlund transition route and set-piece threat, and the fact Portugal needed only a draw. It also acknowledged the price hurdle and withheld final approval. However, the analysis leaned on four wins, attempts and SOT without comparable chance-quality data. That left a material gap in judging how repeatable those wins were.

The later retrieval gives this Portugal-perspective group baseline:

| Earlier match | Portugal xG | Opponent xG | Implication |
|---|---:|---:|---|
| Home to Wales | 1.93 | 0.85 | Positive total, but big chances were 1–3; not uniformly comfortable |
| Away to Norway | 1.04 | 2.52 | Strong support for concern that the winning score flattered Portugal |
| Away to Denmark | 2.25 | 0.76 | Substantial chance-quality advantage; does not support dismissing this win as luck |
| Home to Norway | 1.78 | 0.45 | Positive home performance against that opponent |
| All four | **7.00** | **4.58** | Positive overall, with meaningful variation |

Across the two Norway games Portugal's aggregate was **2.82–2.97**. Across the two home games it was **3.71–1.30**. Excluding the favourable Denmark reverse leaves **4.75–3.82** across three. These overlapping windows are sensitivity checks, not independent confirmations. Four fixtures against three opponents are still a small sample, and current absences can change their relevance.

The data was retrieved after the match from a direct provider route. It must not be inserted into the original pre-match evidence as if it was used then. This establishes a retrieval gap in the audit trail; it does not prove the same endpoint response was accessible at the original cutoff. Differences between UEFA and FotMob attempts/SOT are retained rather than silently combined.

Sources: [both-teams baseline and raw-data references](audit-evidence/both-fixtures-baseline-xg.json); [Norway away](https://www.fotmob.com/api/data/matchDetails?matchId=5181864); [Denmark away](https://www.fotmob.com/api/data/matchDetails?matchId=5181865); [Norway home](https://www.fotmob.com/api/data/matchDetails?matchId=5181867); [Wales home](https://www.fotmob.com/api/data/matchDetails?matchId=5181862).

## What happened in the 1–4 loss

Portugal led SOT **8–6**, yet trailed xG **1.26–2.33**. Removing Denmark's penalty narrows the comparison to **1.26–1.54 npxG**. The scoreline therefore should not be described as four goals' worth of repeatable chance dominance. Equally, eight SOT did not establish Portugal's superiority. First-half Portugal xG was only **0.18**; Denmark's first-half xG was 1.08 including the penalty, or 0.29 excluding it.

Damsgaard assisted one Højlund goal, and Andersen scored a header. Those events are consistent with opponent routes the report had already identified. They do not prove a particular replacement full-back was responsible, or that incentives caused the defeat. Portugal's late goal made the passed BTTS Yes direction land; that is not evidence that it should automatically have replaced the win selection before kickoff.

Portugal lost the ordinary win direction and never took a two-goal lead. Actual bookmaker settlement is not available. Source: [FotMob match record](https://www.fotmob.com/api/data/matchDetails?matchId=5181870), [saved response](audit-evidence/fotmob-match-5181870.json).

The actionable decision error is **not** “Portugal must never be backed.” It is that a positive historical count profile was not sufficient to resolve missing chance quality, changed personnel, opponent routes, draw incentives and price together. An acceptable XI alone would not establish that the 66.67% ordinary win break-even requirement was exceeded. No calibrated win forecast had been produced.

## Sweden: review a winning reserve just as critically

The original four-match shot balance was 43–46 and the home balance 23–29, contributing to a reserve decision. Later comparable data shows **6.74–2.37 xG** across the four games, including **2.94–1.70** at home. Thus a shot-count-only objection understated Sweden's chance quality. This same retrieval improvement can strengthen a case as well as weaken one; it is not a rule for finding reasons to reject favourites.

Sweden then won 3–2 with two penalties. Its match xG was **2.28–1.14**, but non-penalty xG was **0.70–1.14**. Sweden led 3–0 at half-time, so subsequent game state matters too. The result does not establish repeatable open-play dominance or prove that 1.50 offered value. The reserve status remains unchanged.

Sources: [baseline ledger](audit-evidence/both-fixtures-baseline-xg.json), [Sweden result](https://www.fotmob.com/api/data/matchDetails?matchId=5181846), [saved response](audit-evidence/fotmob-match-5181846.json).

## The other international failures expose different mechanisms

On **13 November**, Iceland's 5–0 win produced **one** corner; the Netherlands' 7–0 win produced **five**. Both conditional shortlist corner thresholds missed. The earlier Iceland sample already contained a 3–0 win with two corners. Territorial superiority did not justify treating 5+ corners as the reliable expression of that superiority. The earlier choice between Iceland win around 1.70 and corners around 1.80 lacked a convincing comparative case. The winning outright remains a counterfactual reserve, not a retrospectively selected winner.

On **12 November**, Cucurella recorded **zero tackles**. Spain had 70% possession and his recorded ground-duel involvement was one. Spain's dominance already existed before Czechia's late dismissal. The practical omission was insufficient evidence of tackle opportunities in his zone. It is not enough to claim that a winger is weak, to cite a player's ability to win duels, or to count blocks/clearances as tackles. Exact role, opposition activity, minutes, event definitions and failed comparable observations are essential.

Sources: [Nov13 verification](../2026-11-13/result-verification.json), [market-choice audit](../2026-11-13/archive/friday-13-november-2026-market-choice-audit.md), [Nov12 audit](../2026-11-12/archive/thursday-12-november-2026-results-audit.md).

The November 13 player follow-up is also preserved: Wirtz recorded five shots and Kimmich drew one foul, so the exploratory Germany pair's statistical thresholds were reached; Serbia had two dismissals. McGinn drew one foul in 90 minutes, missing both the separate 2+ watch and riskier 3+ alternative. The seven-of-seven recorded Scotland starting sample for his 2+ line was descriptive, not a guaranteed probability, and the club sample contained unknowns. No player builder had been promoted at that report's cutoff. Sources: [original expanded review](../2026-11-13/archive/friday-13-november-2026-expanded-review.md), [verified player counts](../2026-11-13/audit-evidence/nov13-player-prop-verification.json).

## Changes applied and how to evaluate them

1. Mandatory journal reading and append-only capture for research, refreshes and reviews in all three skills, plus a dedicated journal skill. Preserve research statuses, important passes, zero-final slates, outcomes and source limitations.
2. A bounded decisive-data retrieval check, with comparable chance quality for goal/result finalists and exact event distributions/opportunity for other markets. Missing data can change inclusion; it cannot be silently treated as reassuring.
3. A favourable-XI counterfactual: if an expected lineup would not resolve substantive doubts, use reserve/pass/insufficient evidence rather than presenting a conditional candidate as nearly final.
4. Symmetric opponent/outlier checks, manager/role/availability context, explicit draw and early-lead scenarios, and separation of opportunities from conversion. Keeper/referee/duel evidence is used only where it can change the selected market's mechanism. No invented feature coefficients.
5. Exact-market comparison before switching from a win/BTTS direction; no quota of selections, accumulator target, or assumption that short odds establish safety/value.
6. A prospective process review after four completed research slates. Check implementation and record all outcomes; do not declare success from a short winning run.

The earlier three user-reported winning groups remain in the archive, alongside the Monaco watch that failed, the omitted Brighton direction that won, and the later losses. There is no controlled comparison establishing which analytical features caused the wins. League football may offer a longer stable sample, but manager changes, injuries, price and matchup still require fresh assessment. International failures are not an excuse to assume the same weaknesses disappear next weekend.

See [active lessons](../../journal/active-lessons.md), [journal instructions](../../journal/README.md), [independent method challenge](method-challenge-review.md). The main lead retained interpretation and changes; Luna retrieved/checks facts, Sol challenged the methodology and journal integrity, and Terra implemented the journal backend. No model-specific forecasting edge has been measured.
