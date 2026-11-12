# Build handoff

Choose **GPT-6.1 Sol / High**, open this repository and paste the prompt below. This is a practical lower-cost implementation choice relative to Astra. Keep Luna for small extraction tasks; the lead owns the finished interface. These are workflow recommendations, not guarantees of equal model performance. [Official model guidance](https://learn.chatgpt.com/docs/models).

## Copy-and-paste prompt

```text
Build phases 1–2 of the Matchday research journal in this football-research-skills repository.

Read design/journal/README.md, DESIGN.md, DATA-CONTRACT.md, HISTORICAL-IMPORT.md and WORKFLOWS.md. Inspect design/journal/assets/desktop-concept.png. Written data rules take precedence over abbreviated mockup labels. Keep existing research skills and their usage documentation working.

Implement a polished static HTML/CSS/vanilla-JavaScript site under journal/. Use the specified system typography, restrained green palette, whitespace and panel geometry. Include Journal, Review and Methods, the three skill category tabs, date/status filters, selection detail with Before kickoff / After the match, source ledger, and JSON export. Complete mobile layout, keyboard/focus behavior, reduced-motion support and empty/loading/partial-data/error states. Build real controls, not a screenshot embedded in a page.

Use JSON as the source of truth in Git, with immutable research revisions and separate verification records. Create schemas and a small deterministic validator/index generator. The page is read-only; export downloads a copy and cannot claim to save to GitHub. No account login, client API keys, bookmaker actions or external database.

Use design/journal/historical-inventory.json as an import inventory, not a validated canonical slate file. Start with its three historical slates and 20 entries. Read original saved reports if accessible in the project workspace; otherwise retain honest inventory summaries and mark detailed evidence unavailable. Six Sunday outcomes are documented in a saved audit, not freshly verified by this handoff. Do not invent Thursday/Saturday scores, original forecasts, missing sources, bet placement, profit or early-payout eligibility. Preserve Utrecht–NEC's price pass, Brighton's omission and all original conditions. Historical imports stay out of prospective performance by default.

Where supported, explicitly use gpt-6-luna at medium effort for bounded report extraction, with fixed source files and output fields. Do not give workers the same canonical file to edit. Keep integration, data judgments and final visual quality with the lead. Use a focused reviewer for the completed contract/UI if available. Report models actually used; do not claim skills automatically change the lead or guarantee cheap routing.

Implement only deterministic settlement functions whose required rules and evidence are known. Unimplemented or ambiguous markets return needs-review. Never apply a result-leg promotion to BTTS/corners/player legs, infer a two-goal lead from a 3–2 final score, or multiply singles into a supposed builder quote. Do not create an accumulator by grouping every row on a date. Null forecasts stay null.

Run the acceptance cases below. Inspect the rendered UI at desktop, tablet and mobile widths and fix defects. Preserve the concept's calm hierarchy. Document local preview and validation commands. Complete local implementation and report what works, intentional limitations and verification evidence.

Do not enable an automation or implement the proposed fourth skill during this phases 1–2 request. Do not deploy as a side effect; deployment can be requested after the finished preview is reviewable.
```

## Acceptance cases

### Records

- Three historical slates, 20 logical entries and six documented outcomes; counts derive from records. Fourteen outcomes remain unknown, not losses. Include the Monaco watch without claiming this is every screened game.
- Utrecht–NEC remains a price pass after a documented 2–3. Brighton's omission coexists with its original higher-risk watch label. Neither becomes an approved winning bet.
- Preserve exact fractions; round only for display. Distinguish price hurdle and forecast. Null forecasts cannot generate fake calibration charts.
- Reimporting changes nothing. Refreshes append revisions. Post-match amendments cannot replace the scored pre-match decision; corrections preserve old verifications.
- Sources/references resolve. No private paths, account details, secrets or raw chats enter public data. Missing reports produce a visible limitation.

### Settlement and metrics

- Pass the fictional cases in WORKFLOWS.md: unknown eligibility, 3–2 without chronology, an early-paid result leg with a losing corner leg, Asian/three-way equality, and corrected player statistics.
- Unsupported contracts return needs-review. Missing is not zero. An abandoned match is not a presumed loss.
- Unquoted builders show Joint price pending. Count a builder once in headline entries and show its legs separately.
- Default performance excludes historical/demo records and reserves/passes. Pending/disputed counts remain visible. Score the defined pre-match snapshot once, including handling withdrawn/replaced entries.

### Function and finish

- Combined category/date/status filters work; empty categories are useful. Direct links survive reload. Back/Close restores archive context and focus.
- Missing/malformed JSON produces a visible error and truthful incomplete summary, not a complete zero-entry archive.
- Export contains valid public records/provenance for the visible scope and reports a download, never a remote write.
- Inspect 1440×1000, 1024×768 and 390×844 renders; check 320px and 200% zoom. Capture review images locally. Code inspection alone is insufficient visual verification.
- No overlapping fixture names, prices, badges or evidence text. Dialog keyboard controls work. Status has text plus color. No dead controls or decorative fake graphs.
- Works under a repository subpath without a framework CDN, remote font or secret-dependent startup. Document the local serving command actually used.

## Next phases

After the website, phase 3 adds football-journal, its references and controlled integration into the three research skills. Use WORKFLOWS.md and the implemented schemas. Test capture/verify manually before scheduling. Result checks do not silently rewrite forecasting methods.

Publication can later use GitHub Pages or the requested static host. A deployed static page does not supply a background worker; scheduled verification is a separately configured app task.
