---
name: lead-enrichment
description: Research a list of B2B leads and write personalized cold-email merge variables for every row, then emit a trimmed send-ready CSV. Use this whenever the user provides leads, a lead list, a lead export, a prospect list, an Apollo/ZoomInfo/Lusha CSV, or a Google Sheet of companies and wants them enriched, personalized, researched, or prepared for cold outreach. Also use it whenever they mention fuzzy variables, AI variables, merge variables, reviewDetail, observedResponseGap, or painPointOpener, or ask to "run the usual flow" / "enrich these" / "do the leads" on a batch of companies. Trigger even when they just paste rows of company data without naming the process.
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
