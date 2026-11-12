# Evidence and handoff contract

## Give a retrieval worker a bounded task

Specify the fixture/date/timezone, named players, exact stats, comparable competitions, desired recent window and authoritative sources already discovered. Ask for source URLs and match identities, not recommendations. Give each worker one coherent dataset or independent match; avoid redundant broad research by multiple workers.

Request rows with:

`player, fixture_id, match_date, opponent, venue, competition, starter_or_sub, minutes, role_if_verified, shots, sot, fouls_committed, fouled, tackles, source, retrieved_at, missing_fields, anomalies`

Retain missing fields as null/unknown, explicit zero as zero, and DNP separately. Do not let the worker fill absent stats from memory. A page that loads today's fixture despite an old URL is not a valid historical source.

For prices request:

`book, region, fixture, market_label, player, threshold, single_odds, joint_quote_or_null, observed_at, source, settlement_notes`

Preserve blank cells when extracting column-oriented odds grids; otherwise one missing price shifts every later player's price. Verify row names and column headers together. Record a real joint quote only after the exact combined selections are visible. A price-comparison listing or arithmetic product must be labeled accordingly.

## Lead review

Check fixture identity and the decisive rows against the original source or saved artifact. Audit apparent perfect streaks, zeros, start/sub labels, conflicting providers and unexpectedly generous prices. A worker should identify uncertainties, not silently resolve them in the favorable direction.

Compute threshold counts using the actual denominator. If source omission conventions are unknown, report known successes, known failures and missing observations separately. Keep club/national samples apart. Show both the original sample and any justified sensitivity exclusion.

Use the relevant market rules from the bookmaker's current regional help pages. Rules and promotions change; preserve observation dates and do not hard-code a historical policy as permanent.

## Compact final research structure

1. Fixture inventory and coverage: which games received deep player research.
2. Pair table: two exact selections, individual odds, actual joint quote or pending, status and XI condition.
3. Per-pair evidence: national/current-context counts with minutes; separate club/baseline corroboration; tactical inference; strongest counterargument.
4. Alternatives rejected or reserved: especially higher thresholds and unavailable markets.
5. Final decision conditions and sources. Do not provide a numeric probability unless it was genuinely modeled and justified.

Keep routine retrieval detail in a linked ledger when the main answer would become unwieldy. Thoroughness means checking decision-changing assumptions, not maximizing the number of metrics or pages.

## Review record

Save a pre-match timestamp, exact line/quote, status, evidence, counterargument, XI condition, method version and numerical forecast only if one existed. Afterward append actual counts and settlement, including replacement players, void legs and promotional exceptions. Keep the original decision intact. Do not retrospectively turn a research reserve into a successful recommendation.
