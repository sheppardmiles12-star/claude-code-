# Handoff: nationwide roofing scrape

The Apify connector stopped registering in the session where this was set up.
Everything below is ready to run in a fresh session that has apify enabled.

## Paste this into a new session

> Run the lead-enrichment skill. Scrape roofing nationwide using the input at
> `outreach/apify/roofing_us_v1.json`, then run the 20-lead ICP gate and tell me
> the score before enriching anything.

The skill at `.claude/skills/lead-enrichment/` already carries the filter policy,
the ICP definition, the 75% gate, the email template and both variants, and the
emit/validate scripts. Nothing needs re-explaining.

## Staged inputs

- `outreach/apify/roofing_us_v1.json` , plain `roofing` keyword, US-wide, 1-30
  staff, owner/founder/president/CEO/GM/partner/director, 100 leads.
- `outreach/apify/roofing_us_v2_excludes.json` , same plus excludes for
  manufacturing, supply, distribution, staffing, insurance, landscaping and turf.
  Use this if the 20-lead gate comes in under 15. Those excludes are drawn from
  the actual misses in the Washington roofing data, not guesses.

## Two traps that cost money here

**A free `countOnly` run consumes the cursor for that exact filter set.**
`dontSaveProgress: true` does not prevent it. The next real scrape on the same
filters returns `status: end_of_saved_search` and few or no leads. `resetProgress:
true` sometimes clears it and sometimes does not; changing a keyword to force a
new fingerprint is the reliable cure. This cost us an HVAC run. Either skip the
count when the pool is obviously large, or count on a different keyword from the
one you intend to scrape. Nationwide roofing does not need a count.

**`itemCount` in the run response is stale.** Runs reporting 0 items have come
back with full result sets (HVAC reported 0, actually had 192). Always fetch the
dataset before concluding a niche is empty.

## What is already done

- `outreach/electrical_wa_enriched.csv` , 100 scraped, 14 pass ICP, 6 send-ready
- `outreach/multiniche_wa_enriched.csv` , HVAC / water damage / plumbing,
  20 rows, 10 send-ready
- `outreach/leads_send_ready.csv` , the original 55 Washington leads,
  23 send-ready, on the older ICP and an older template
- `outreach/apify/niche_counts_wa.csv` , free market-size counts for 15 niches

## Open decision

Roughly a quarter of ICP-qualified leads in every batch died on `emailStatus`
being `pattern_match`, `catch_all`, or blank. The ICP requires a verified email
but the filter policy says never filter on `emailStatus`, so we pay to scrape
addresses that are then discarded. Nationwide the pool is effectively unlimited,
so filtering costs nothing that cannot be replaced. Worth revisiting.
