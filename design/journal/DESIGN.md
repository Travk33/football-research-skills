# Matchday visual and interaction specification

## Character

Quiet, precise, spacious. An editorial research journal with the restraint of a well-made desktop app. Football is expressed through fixture names, a tiny pitch mark and structured evidence. Avoid sportsbook styling, neon, flashing live badges, giant payout figures, decorative charts, stock photographs and team-crest licensing dependencies.

Use [the original concept](assets/desktop-concept.png) as the desktop visual target. Build real text and controls. Do not reproduce generated-image imperfections or rely on its abbreviated data labels. All views share the same typography, spacing and status language.

## Tokens

| Token | Value | Use |
|---|---|---|
| canvas | #F5F5F7 | Page background |
| surface | #FFFFFF | Archive and evidence panels |
| text | #1D1D1F | Headings and body |
| text-secondary | #667069 | Supporting text, subject to contrast check |
| border | #DDE2DE | Quiet structural dividers |
| accent | #185A45 | Active navigation and primary controls |
| accent-soft | #EDF4EF | Selected row background |
| link | #0064CC | Links on light surfaces |
| caution / caution-soft | #865300 / #FFF3D9 | Conditions, price passes, review needed |
| negative / negative-soft | #A52D35 / #FCEEEF | Losing result or error; never a judgment about the user |
| focus | #0071E3 | Visible focus outline |
| panel-radius / control-radius | 16px / 10px | Shared geometry |
| panel-shadow | 0 3px 18px rgba(29,29,31,.035) | Sparse depth; no heavy drop shadows |

Use system fonts: `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`. Do not download Apple's proprietary font. Body 15px/1.55; secondary 13px/1.45; fixture 15px/600; page title 32px/1.15/650; metric value 30px/600. Mobile body remains at least 15px, inputs 16px. Numeric columns use tabular figures. No letter-spaced all-caps paragraphs; small eyebrows may use 11px/600 with 0.06em tracking.

Spacing scale: 4, 8, 12, 16, 20, 24, 32, 40, 48px. Panel padding 24px desktop, 16px mobile. Primary targets 44px high. Icons 18–20px and visually consistent; use simple local SVGs with accessible names where needed. No remote icon/font dependency.

## Information architecture

- **Journal:** category, dates and decision filters; archive list; evidence detail.
- **Review:** verification queue, historical/prospective separation, outcomes and proposed lessons.
- **Methods:** three skill cards linked to their actual repository files; version information and a short account of what each method checks.

The three category tabs are present on Journal and Review. Use labels **Wins & BTTS**, **Other markets**, **Bet builders** in that order; stable stored keys are defined in DATA-CONTRACT.md. Categories are not separate copies of the same records. A builder belongs to Bet builders; its atomic legs are nested, not additional headline picks in other tabs.

## Desktop: 1280px and wider

Left navigation 216px wide, viewport-height on large screens; content flows vertically. Top brand area has a 22px outlined pitch symbol, Matchday, and Research journal below. Active navigation has a forest-green background and white text. Footer shows the latest data update with its timezone, not the user's current time disguised as a data refresh.

Main content padding 40px, usable maximum width 1440px, centered beyond that. Breadcrumb and export sit on a slim top row. Main title/subtitle align left; date-range control aligns right. Segmented category control spans the working area, with equal readable hit targets. Under it, three equal summary tiles separated by 16px gaps.

The archive/details area uses `minmax(0, 1.55fr) minmax(340px, 1fr)`, 24px gap. Archive is one white panel with a heading, date chips and a row list. Default active date is the latest available date within the chosen category; an exact hash link overrides it. Do not select a historical date simply because it appears in the reference image.

Each row has: small team-initial monogram; fixture + selection; reference price; original decision badge; compact outcome and evidence state. Price is right-aligned. Result colors never recolor the original decision badge. Use a visible selection button, not an inaccessible clickable div. Row height is content-driven, normally 76–92px. Long names wrap; icons never replace essential words.

Selected row: very pale green fill, 3px forest indicator, visible selected state. Focus has its own blue ring. Hover is a subtle fill only. No layout movement or bouncing cards.

## Evidence detail

Top: fixture, category/market, original decision, original reference odds. For a binary contract without pushes or partial settlements, place its break-even percentage beneath the price with the caption **Price hurdle, not our forecast**. Otherwise show a settlement-aware explanation rather than an unconditional 1/odds hurdle. Only show a separate forecast when it was actually recorded with its method before kickoff.

**Before kickoff** contains:

1. Original decision and source report date; distinguish exact, approximate and unknown timestamps.
2. Why considered: concise arguments with source anchors, relevant sample sizes and measured facts.
3. What could defeat it: strongest counterargument and outstanding lineup/price conditions.
4. Evidence table: metric, team/player, period, sample, provider and interpretation; no unsourced decorative radar charts.
5. Changes before kickoff: revision timeline and explicit user inclusion/omission when documented.

**After the match** contains:

1. Match state and result, plus evidence level: documented, verified, disputed or pending.
2. Ordinary outcome and any separate eligible promotion outcome; bookmaker settlement remains unknown without evidence.
3. Relevant goal chronology or player statistics, with sources and verification time.
4. What the result teaches: process observations and limitations; distinguish factual verification from a proposed method change.

A quiet result preview may appear under the original decision, as in the concept. The full after-match view provides the supporting detail. The original decision is never replaced with a green Won pill. On Utrecht–NEC, **Price pass** remains even if the documented BTTS outcome is Won.

Builders show two or three numbered legs, their exact definitions, minutes assumptions, actual combined quote or **Joint price pending**, and a short dependence explanation. Display any void/repricing uncertainty explicitly. Do not calculate a displayed builder quote by multiplying singles.

Source ledger opens as a lightweight drawer/dialog containing source title, provider, URL, published/accessed times and the specific supported facts. Raw chat content and account screenshots never appear. Opening a source in a new tab must be communicated by the link label/icon.

## Review and Methods

Review starts with a compact queue: **Needs result**, **Needs rule check**, **Disputed source**, **Ready for review**. Show counts derived from data. Below, separate **Historical archive** and **Prospective record** with an explanation of each denominator. Initial release displays documented/verified coverage; a 100% win graphic is inappropriate for the unverified retrospective import.

When prospective data exist, show resolved wins/losses alongside pushes/voids/pending counts and sample size. Ordinary outcomes and promotion-adjusted outcomes have distinct labels. Show no calibration chart where numerical forecasts are missing. Any later chart needs a table alternative and transparent cohort filters.

Lessons are simple records: observation, supporting selection links, proposed change, review status and method version. Methods cards link to the three actual skills and current usage guide. A future Journal skill can appear when implemented; until then describe capture as planned in documentation, not as a working button.

## Tablet and mobile

At 900–1279px: use a compact top navigation instead of the side rail. Main padding 24px. Archive fills width; selection opens an accessible side drawer up to 520px. Closing it restores focus to the selected row.

Below 900px: single-column layout, 16px gutters. Header title 28px. Navigation becomes three text tabs: Journal, Review, Methods. Category control wraps its labels to two lines if needed; all three remain reachable at 320px without horizontal page scrolling. Date/filter controls wrap to separate rows. Summary tiles become three compact cells if they fit or a vertical stack below 380px.

Rows become stacked cards inside the archive panel: fixture and result on top, selection below, price and decision on the final line. No shrunken desktop table. Evidence opens in a full-width dialog with a visible Back/Close control and natural scrolling. Sticky dialog header may contain fixture and close; it must not obscure keyboard focus. A hash/deep link can load details directly, and browser Back returns to the archive context.

## States and behavior

| State | Required presentation |
|---|---|
| Empty category | “No entries yet” plus a sentence explaining which research belongs here; no invented fixtures |
| Filter has no matches | “No entries match these filters” with Clear filters |
| Loading | Neutral placeholder lines, brief accessible loading announcement; reduced motion respected |
| Fetch/parse failure | Clear failure message and Retry; never turn the error into zero entries |
| Partial data failure | Render validated available records with a visible warning; exclude incomplete totals from performance calculations |
| Missing odds/probability/result | “Not recorded”, “No forecast recorded”, “Pending verification” as appropriate; never 0 or 0% |
| Disputed result | Amber review label, both source claims visible; excluded from resolved metrics |
| Historical import | Persistent historical label; access to provenance and limitations |
| Stale data | Show the last verification time; no fake live dot or autonomous refresh claim |

Hash/query state should preserve category, date, selection and view so links can be shared. Local storage is for UI preferences only. Export downloads the selected public records and relevant provenance with a clear filename/date; it never claims the remote archive was saved. No sign-in, betting action or direct bookmaker transaction controls.

## Accessibility and finish

Use semantic headings, landmarks, links, buttons and tables. Implement proper keyboard tab behavior with arrow keys, active state and labeled panels. Dialogs trap focus, close with Escape and restore focus. Announce filter count changes politely without reading every row. Statuses always include text; color is supplementary.

Verify normal text contrast at least 4.5:1 and meaningful control boundaries/focus at least 3:1 on their actual backgrounds. Neutral dividers may remain subtle because they are not the sole indication of a control. Keep 44px touch targets. Support 200% zoom, 320px width and prefers-reduced-motion. Transitions 120–180ms only for state changes; no animated counters or automatic carousels. Light mode is the finished v1 target; do not add an unfinished dark theme.

Inspect actual rendered pages at 1440×1000, 1024×768 and 390×844, plus a 320px/200% zoom check. Compare the desktop against the concept for spacing, hierarchy and restraint. Check mobile details and empty/error states as carefully as the ideal screenshot.
