# Review and improve prospectively

Use when checking results, maintaining a method or assessing whether a claimed winning streak demonstrates skill.

## Preserve the original prediction

Record before kickoff: timestamp/timezone; fixture; competition; market and settlement terms; offered price/book/time; status; core evidence; strongest counterargument; lineup condition; method version; and numerical forecast only if one genuinely existed. Record screened passes as well as selections. Missing odds or probabilities remain missing.

Do not rewrite a reserve or price pass as a recommended winner after the event. Distinguish user-reported returns, verified settlements and a separately declared fixed-stake hypothetical. Never infer personal profit merely from match scores.

## Separate three questions

1. **Settlement:** what happened under the exact contract, including voids, pushes, early payout and replacements? A match result may differ from promotional settlement.
2. **Process:** were fixture identity, availability, minutes, sources and market definitions correct? Did the material counterargument occur? Was the forecast based on repeatable chance production or a distorted result streak?
3. **Forecast quality:** did a sufficiently large, prospectively recorded set of probabilities behave as predicted? One close win or loss provides limited evidence.

Use all qualifying decisions from a predeclared period, not a selection of winners. Assess descriptive hit rates with denominators and uncertainty. Evaluate profit only using complete prices/settlements and a declared staking basis. Report dependence between legs and slates; three successful accumulators are not a large independent sample.

If probabilities were recorded before matches, use calibration, Brier score or log loss as appropriate and compare with a sensible baseline. Do not reconstruct probabilities from later narratives. Compare closing prices only for the same bookmaker/market/line/rules where feasible. Price movement alone is not proof of profitability.

## Change the method narrowly

Describe the observed failure mechanism, the proposed correction, affected markets and a prospective evaluation window before using results to judge it. For example, checking red-card timing repairs a specific data distortion; “always avoid teams that nearly lost once” overfits a single outcome.

Retain a versioned record of the previous rule and the reason for the change. Test new thresholds and market families separately; success in match winners does not validate player tackle builders. Avoid collecting more metrics without explaining what decision they can change.

## Decision ledger format

A compact Markdown table or structured file is sufficient. Suggested fields:

`decision_id, recorded_at, kickoff, fixture, market, line, book, region, odds, quote_time, status, source_links, evidence, counterargument, xi_condition, forecast_probability_or_null, model_or_method_version, result, settlement, closing_odds_or_null, review_note`

Keep the pre-match fields immutable; append revisions with a new time and reason. The review should explain what was learned without treating luck as validation or every loss as a methodological failure.
