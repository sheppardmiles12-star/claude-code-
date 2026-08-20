---
name: lead-enrichment
description: Scrape B2B leads from Apify and/or research them and write personalized cold-email merge variables for every row, then emit a trimmed send-ready CSV. Use this whenever the user names an ICP to scrape, asks to pull or find leads, or provides leads, a lead list, a lead export, a prospect list, an Apollo/ZoomInfo/Lusha CSV, or a Google Sheet of companies and wants them enriched, personalized, researched, or prepared for cold outreach. Also use it whenever they mention fuzzy variables, AI variables, merge variables, reviewDetail, observedResponseGap, or painPointOpener, or ask to "run the usual flow" / "enrich these" / "do the leads" on a batch of companies. Trigger even when they just paste rows of company data without naming the process.
---

# Lead enrichment for cold outreach

This skill turns a raw lead export into a send-ready CSV where the personalized
fields read like a human wrote them after actually looking the company up.

The whole value of this flow is that the personalized segments are **true**. A
prospect can tell in one line whether you looked them up or ran a mail merge.
That is why the research step is not optional, and why rows without evidence get
held back rather than filled with something plausible. One held row costs
nothing. One invented review detail costs the domain.

## The email this feeds

Subject line is just `{{firstName}}`. Plain, no hook, no teaser, so it looks
like a person emailed rather than a campaign.

**Standard variant** (use whenever a usable positive review exists):

```
heyy {{firstName}}, 

saw {{businessName}} recent review where {{reviewDetail}}, and wanted to say hi.

i run a b2b automation agency where i catch the calls/leads that come in after hours or via form so they dont just sit there til someone gets around to it. figured worth a shot since {{observedResponseGap}}.

ive done my homework on you guys and believe i can help out {{businessName}}. are you open to finding out more? if so it'd take no more than 15 min over the phone to break it down for you.
miles
```

**Negative-review variant** (only when no usable positive review exists). The
framing around the variable changes, not just the variable, because "wanted to
say hi" doesn't pair with pointing out a problem. Note the greeting runs inline
here and the signoff sits on its own line:

```
heyy {{firstName}}, read through {{businessName}} reviews {{reviewDetail}}.

i run a b2b automation agency where i catch the calls/leads that come in after hours or via form so they dont just sit there til someone gets around to it. figured worth a shot since {{observedResponseGap}}.

ive done my homework on you guys and believe i can help out {{businessName}}. are you open to finding out more? if so it'd take no more than 15 min over the phone to break it down for you.

miles
```

## Sourcing leads from Apify

When the user names an ICP rather than handing over a file, scrape it first with
the Apify actor `pipelinelabs/leads-finder-with-emails-apollo-lusha-zoominfo`
(there is a dedicated tool for it; no need for `call-actor`). Its output columns
match the enrichment schema directly.

### Standing filter policy

These are the user's rules, learned from what actually converts. Deviating
quietly wastes their money, so follow them and say so if you think one is wrong.

**Use:**
- `companyKeywordIncludes` , the primary targeting lever. Simplest thing that works.
- `personTitleIncludes` , founder, co-founder, owner, co-owner, partner,
  co-partner, president, ceo, director. Set `includeTitleVariants: true` so
  CEO and Chief Executive Officer both match.
- `seniorityIncludes` , `owner`, `c_suite`, `partner`, `director`. Founder and
  co-founder have no seniority enum, which is why titles carry them.
- `roleMatchMode: "any"` , these are alternatives, not requirements.
- Company size roughly 1 to 30 staff. `companyEmployeeMin: 1` with
  `companyEmployeeMax: 30` is tighter than the buckets, whose nearest option
  (`11-50`) overshoots to 50.

**Do not use unless the user explicitly asks:**
- `annualRevenue*` , revenue banding
- `emailStatus*` , email verification
- `companyIndustry*` , industry
- `companyLocation*` , location

Location is currently an explicit exception: **Washington state only**, so
`companyLocationStateIncludes: ["Washington"]` applies until told otherwise.

Leaving `emailStatus` unfiltered means unverified addresses come through. That
is the user's call and it does raise volume, but it also raises bounce rate on a
cold domain, so it is worth a mention when a batch looks heavily unverified.

### Validate filters before spending

There is also a browser-based Lead Viewer at `https://viewer.pipelinelabs.dev`
that shows a live match count and exports the exact JSON. Point the user at it
when the MCP connector is unavailable, since it needs no tooling on this side.

`countOnly: true` runs a free count: no extraction, no charge. Use it to check a
filter set returns a sane number before any paid run. Filters that are too
narrow return zero and burn the run for nothing.

Set `dontSaveProgress: true` on validation and test scrapes. The actor keeps a
cursor between runs, so a throwaway test would otherwise advance past leads the
real run should have picked up. Leave progress saving on for the accepted final
run so the next day's pull continues rather than repeating.

`waitSecs` caps at 45 seconds. A 100-lead run usually exceeds that, so poll
`get-actor-run` until terminal, then pull rows with `get-dataset-items`.

### What counts as in-ICP

The user's definition, parameterised by whichever niche the run is targeting.
Substitute the niche for `{{niche}}` and apply it in the 20-lead sample and in
any filter revision:

- **A real `{{niche}}` company.** `{{niche}}` is the company's primary or
  exclusive trade. Not a supplier or manufacturer, not an insurance or adjuster
  firm, not a general contractor that mentions `{{niche}}` in passing, and not a
  multi-trade exteriors or insulation business where `{{niche}}` is one line
  among several.
- **A reachable decision-maker.** Owner, president, CEO, or GM, not a random
  employee. The email is real and verified, not guessed or an unrelated personal
  address.

Email verification is judged here rather than filtered upstream, because the
user does not want `emailStatus` narrowing the pool. In the output data,
`emailStatus: deliverable` is the good value.

The "primary trade" half is what the sample usually turns on, and it bites
differently per niche. Roofing pulls in multi-trade exteriors firms; electrical
pulls in electrical *manufacturers* and industrial contractors; gutters and
siding overlap heavily with roofers. Name the specific pattern the misses share
when reporting a failed gate, because that is what tells the user which keyword
to exclude next.

**Each niche needs its own gate.** A different keyword is a different search
with different noise, so a pass on one niche says nothing about the next. Never
carry a score across niches, and never enrich a niche that has not passed on its
own sample.

### Check the pool size before scraping

The free count returns the *total* matching pool, not just what a run would
return. If the pool is barely larger than the number of leads wanted, the ICP
gate has nowhere to go: tightening the filters after a failed sample would drop
the pool below the target. Say so before scraping rather than after, because the
options at that point are to widen the ICP, widen the geography, or accept a
smaller batch, and all three are the user's call.

Also watch for overlap with leads already enriched. A pool this size will mostly
return the same companies as last time, so check new results against prior
batches before paying to enrich them again.

### Widening a pool that is too thin

Work the levers in this order, re-running the free count at each step and
stopping as soon as the pool is comfortably larger than the target. Order
matters: each step costs more ICP precision than the one before it, so stopping
early keeps the sample score high.

1. **Raise `companyEmployeeMax`.** Usually the most restrictive filter and the
   cheapest to relax, since the user's size band is approximate ("twenty or
   thirty or so"). Going past about 50 starts pulling in companies big enough to
   already staff a front desk, which is the opposite of the pitch.
2. **Drop `personTitleIncludes` and run on `seniorityIncludes` alone.** The
   free-text title list and the seniority enum filter the same thing twice, and
   the list can miss variants the enum catches.
3. **Add keyword variants** (`roofer`, `roof repair`, `roofing contractor`).
   This widens the most and drifts the most: broader roofing keywords pull in
   suppliers, manufacturers and multi-trade exteriors firms, which the ICP
   excludes. Expect the sample score to fall.
4. **Stop and talk to the user.** If the pool is still thin after the above, the
   geography or the trade is the binding constraint, not the filters. More
   tuning will not fix an exhausted market. Offer a second state, a second
   trade, or a smaller batch, and let the user choose.

Never widen by re-enabling a filter the user turned off (revenue, email status,
industry) or by quietly expanding geography. Those are policy, not tuning.

### The ICP quality gate

Scrape quality decides everything downstream, so check it before enriching.
Enriching a bad scrape burns roughly two web searches per lead on companies the
user never wanted.

1. Scrape 100 leads (or the number the user gave; default 100).
2. Take 20 of them and judge each against the stated ICP: right kind of
   business, decision-maker title, size in range, and a real operating company.
3. **15 or more of 20 in ICP (75%)**, the scrape is good. Proceed.
4. **Fewer than 15**, something is wrong with the filters. Say what the misses
   have in common, revise, and re-scrape. Keyword breadth is the usual culprit:
   a keyword that also matches suppliers, manufacturers, or consultants pulls in
   businesses that don't field inbound service calls.
5. Only run the full scrape and the full enrichment once the gate passes.

Report the sample honestly. A 12 of 20 that you talk up as fine costs the user a
whole enrichment run.

## Process

### 1. Load and dedupe

Read the input (CSV, Google Sheet via the Drive connector, or pasted rows).
Watch for a base64-wrapped body on Drive exports, decode before parsing.

Research at the **company** level, not the row level. Lead exports routinely
carry two or three contacts at one company. Look each company up once and reuse
the evidence, but **reword the variables per contact** so two people at the same
firm who compare notes don't see an identical mail merge.

### 2. Research each company

Two independent pieces of evidence are needed per row. One good search usually
returns both:

```
"<Company>" <City> <State> reviews communication response business hours contact
```

Direct site fetches are often blocked by network egress policy; search-engine
summaries of those pages are an acceptable substitute. Keep the source of each
quote in your working notes and flag in the summary when a quote came via a
search index rather than the live page, so the user knows what to spot-check.

**Evidence A: a review about communication, speed, or responsiveness.**
Never craft or quality. "They communicated well" is usable; "the roof looks
great" is not. Praise that blends workmanship with general service ("quality of
work and customer service were amazing") is too entangled to use, hold instead.

**Evidence B: a real, checkable response gap.** Posted hours, contact-form-only
setups, a self-stated response window, a 24/7 claim with nothing behind it.

While researching, also note anything that makes the row unsafe to send:
permanently-closed listings, expired licences, rebrands, a `firstName` that
doesn't match the mailbox, or a company whose location contradicts the sheet.
These are worth more to the user than another email.

### 3. Write the variables

`businessName`, how a person would say the company out loud. Scraped exports
are usually lowercased ("anytime roofing") which reads badly mid-sentence, and
long legal names ("SQI Inc Roofing and Restoration") get clunky when the
template repeats them twice. Shorten to the spoken form.

`reviewDetail`, the one variable both variants share, so what it has to complete
depends on which one the row is using. Standard: "saw {{businessName}} recent
review where ___". Negative: "read through {{businessName}} reviews ___". Full
casual clause either way, not a fragment.

`observedResponseGap`, completes "figured worth a shot since ___". Must trace
to Evidence B.

The strongest angle in this ICP is **claim versus reality**: a business
advertising 24/7 or emergency availability with no actual capture mechanism
behind it. If a company claims round-the-clock service, check what really
catches a 2am call. A voicemail box, a form, or nothing at all is the angle.
Don't let the "skip the hours angle if no hours are posted" rule cause you to
miss this, a 24/7 claim *is* the evidence.

Only skip the hours angle entirely when there are no posted hours, no
availability claim, and no contact-mechanism evidence at all. Then the row gets
held.

On a negative row, frame the finding as a fixable cost, never a personal
callout. "This is costing you something," not "you're bad at this." No quoting
the complaint, no naming the customer or incident. The template already supplies
"read through {{businessName}} reviews", so the variable picks up from there,
which is why the negative form usually wants a connector like "and" up front.

- Good: "and a couple of them point at things taking a while to come back, which usually says process rather than anything else"
- Good: "and it looks like response time might be costing you a job here and there"
- Bad: "and you are clearly bad at responding to people". Reads as judgment about them rather than about a process.

On negative rows `reviewDetail` and `observedResponseGap` will often point at
the same underlying gap. Don't say it twice. Let the opener carry the point and
keep the gap to concrete evidence, hours or contact mechanism, rather than
repeating "people said you're slow".

### 4. Voice

Lowercase. Contractions without apostrophes (dont, doesnt, ive, youre, theres).
No corporate phrasing. **No em dashes or en dashes anywhere**, they're the
single clearest tell that a machine wrote the line.

Vary sentence structure across the whole batch. This matters more than it
sounds: these send as a group, and a batch where every gap reads "X to Y is
their window, so Z has to wait" is a detectable template even though each line
is individually true. Before finalizing, read the gap column top to bottom and
rewrite anything that rhymes with its neighbours. Watch especially for repeated
attribution openers ("a customer said" five times) and for a repeated
"nothing + time phrase" construction.

### 5. Hold anything you can't evidence

Set `send_ready` to `no` and write a specific `hold_reason` naming what was
missing, "no posted hours found to pair with the review", not "insufficient
data". The user acts on these reasons, so name the actual gap and any data
problem worth fixing at source. Keep held rows in the CSV.

### 6. Emit the CSV

Use `scripts/emit_csv.py`, which writes the exact column set and runs the
validation gate. Never hand-roll the column order, the user's sender maps
against it.

```
firstName, lastName, email, phone, companyName, businessName, companySize,
annualRevenue, companyCity, companyState, companyCountry, personCity,
personState, personCountry, email_variant, send_ready, hold_reason,
reviewDetail, observedResponseGap, subject, emailBody
```

`subject` and `emailBody` are rendered by the script from the variables and the
template above, not written by hand. That keeps the sent message and the
variables from ever disagreeing: fix a wording problem in the template and every
row follows. Held rows get both left empty so a bad row cannot be sent by
accident.

Then run the validator and fix anything it flags before showing the user:

```bash
python3 scripts/emit_csv.py --validate <output.csv>
```

It checks that no dashes slipped in, that ready rows carry both required
variables, that variant and field population agree, that held rows carry a
reason, and that no attribution opener repeats too often across the batch.

## Reporting back

Lead with the counts (ready / held, and the variant split), then the rows worth
the user's attention: the strongest angles found, and any data problems that
need fixing at source. Don't recite every row, the CSV is the deliverable.
