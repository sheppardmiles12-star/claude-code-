# ICP quality gate: roofing, United States

Two scrapes, both gated on a 20-lead sample against the roofing ICP
(roofing is the primary trade + reachable decision-maker on a verified email).
Threshold is 15/20.

## Run 1 — `roofing_us_v1.json`

- Run `vrPCt8ZiHNGU407B6`, dataset `HJydaMQlwyZ3xJYnr`, 100 leads billed.
- Pool: 7,120 nationwide. Plenty of headroom, so tightening was free.
- **Gate: 2/20 (10%). FAIL.**

What the 18 misses shared, in order of size:

| Pattern | Count | Examples |
|---|---|---|
| Multi-trade exteriors / remodeling (roofing is one line among siding, windows, gutters, painting) | 8 | Johnson Construction, Phillips Home Improvements, Siding Unlimited, Abby Windows, Marshall Building & Remodeling |
| Solar (roofing+solar or pure solar) | 4 | Rooftop Solar, TruHome Pros, BYLTup, Circle L Solar |
| Sells *to* roofers: suppliers, manufacturers, software, co-ops | 4 | Interactive Hail Maps, Gulf Coast Shelter, Meta Team, EDI |
| General contractor / restoration | 1 | Stellar Restoration Services |
| Unverified email | 1 | Encompass Rooftop Services |

Root cause: `companyKeywordMode` defaults to `broad` and matches the company
**description**, not just the name. Every business whose blurb mentions the word
"roofing" qualifies, including everyone who sells to roofers.

## Run 2 — `roofing_us_v3_trade_purity.json`

The staged `roofing_us_v2_excludes.json` targets the supplier/insurance family
but not the two biggest buckets (multi-trade exteriors, solar), so it was
extended rather than run as-is: added `solar, siding, window, gutter,
remodeling, remodel, painting, exteriors, restoration, consulting, consultant,
coatings, adhesive, lumber, marketing`.

- Run `MWj36g7dxiQ4fEXbf`, dataset `mGgwtRj5tpS2xH4QD`, 100 leads billed.
- **Gate: 5/20 (25%). FAIL.**

The excludes worked on the thing they targeted. Trade purity went from ~3/20 to
**13/20** — the sample is now mostly genuine roofing contractors. What fails the
gate now is the *other* half of the ICP: the email.

Email status across the 20-lead sample:

| emailStatus | Count |
|---|---|
| deliverable | 7 |
| catch_all | 8 |
| unavailable | 3 |
| blank | 2 |

Ten of the sample rows are real roofing companies with a real decision-maker
that fail only because the address is `catch_all` or `unavailable` — Texas
Traditions Roofing, Mighty Dog Roofing, Scott Roofing, Castle Crest Roofing,
Rhynehart Roofing and others.

**This is a policy decision, not a filter bug.** `emailStatus` is on the
do-not-use-without-asking list, so it was left off. Turning on
`emailStatusIncludes: ["verified"]` would very likely clear the gate, at the
cost of pool size — and it is the user's call, because it trades volume against
bounce rate on a cold domain.

## Data problems worth fixing at source

Independent of the gate, run 2 carries a lot of field-level noise:

- **`companyName` is wrong on several rows** while the domain and description are
  right: `lone star global trading company` → Paragon Roofing,
  `side hustle threads` → Bunton Roofing, `123 gutters` → 22nd Century Roofing,
  `aventi group llc` → RoofDog, `emerge energy` → Beck Roofing.
- **Email on a different company's domain**: `jamiewhite@kw.com` for Pinnacle
  Roofing (Keller Williams), `steven.moore@nederman.com` for OmniMax Roofing,
  `markschwab@lonestarcdj.com` for Highline Roofing,
  `mitchell.madison@veriforce.com` for Cut-Out Construction.
- **First name does not match the mailbox**: Dale Manus on `mattmanus@`,
  Eskola Ben on `beskola@` (name fields reversed).
- **Company vs person geography contradicts**: Giles Construction (company GA,
  person OH), Jack the Roofer (company CO, description Southern California),
  Quality Assurance Roofing (company TX, description NW Arkansas).

## Decision: verified only

Confirmed by the user. `emailStatusIncludes: ["verified"]` is now standing
policy, staged as `roofing_us_v4_verified_only.json`. The actor's own schema
defines Verified as "confirmed deliverable" and Unverified as "pattern match,
unavailable, catch all", which lines up exactly with the ICP's email test, so
the gate's email half moves upstream into the filter.

### What this costs in volume

Counted across all 100 rows of run 2, not just the 20-lead sample:

| | Count |
|---|---|
| Rows returned | 100 |
| `deliverable` | 45 |
| `catch_all` | 33 |
| `unavailable` / `pattern_match` / blank | 22 |

The 20-lead sample happened to show 35% deliverable; the full batch is 45%.
Either way roughly half the raw pool disappears.

Deliverable alone is not send-ready. Of those 45, a chunk are suppliers and
services that survived the keyword excludes (sheet metal fabrication, permit
expediting, spray foam, a marketing agency, a roofing co-op). Applying the trade
half of the ICP on top lands the end-to-end yield near 30%, and enrichment holds
took a further 3 of 18 in this batch.

**Planning number: budget about three 100-lead runs per 100 send-ready leads.**

### Volume is probably fine, but it is unconfirmed

The nationwide roofing pool was 7,120 before the trade excludes. The post-exclude
pool was never counted, because a free count consumes the cursor for that
fingerprint and the batch was going ahead regardless. So the honest position is:
45% of what run 2 returned was deliverable, and nothing yet measures the verified
pool directly.

Run a `countOnly: true` check on the v4 filter set **using a deliberately
different keyword** before committing to a multi-run batch. If the verified pool
comes back comfortably above a few hundred, volume is a non-issue and no pool
change is needed. If it comes back thin, the levers in preference order are a
second trade or a second geography, not relaxing verified.
