# Cold email template (v2)

**Subject:** `{{firstName}}`

```
heyy {{firstName}}, 

saw {{businessName}} recent review where {{reviewDetail}}, and wanted to say hi.

i run a b2b automation agency where i catch the calls/leads that come in after hours or via form so they dont just sit there til someone gets around to it. figured worth a shot since {{observedResponseGap}}.

ive done my homework on you guys and believe i can help out {{businessName}}. are you open to finding out more? if so it'd take no more than 15 min over the phone to break it down for you.
miles
```

## Negative-review variant

Use only when no positive review exists. Tag the row `email_variant: negative_review`.

```
heyy {{firstName}}, 

{{painPointOpener}}.

i run a b2b automation agency where i catch the calls/leads that come in after hours or via form so they dont just sit there til someone gets around to it. figured worth a shot since {{observedResponseGap}}.

ive done my homework on you guys and believe i can help out {{businessName}}. are you open to finding out more? if so it'd take no more than 15 min over the phone to break it down for you.
miles
```

## Merge columns the sheet needs

| column | notes |
|---|---|
| `firstName` | already in the sheet, drives both subject and greeting |
| `businessName` | clean display casing, not the lowercase scrape value |
| `reviewDetail` | communication / speed / responsiveness only, never craft |
| `observedResponseGap` | real posted evidence only |
| `painPointOpener` | negative variant only, blank otherwise |
| `email_variant` | `standard` or `negative_review` |
| `send_ready` | `yes` / `no` |
| `hold_reason` | why a `no` row was held |
| `review_evidence` | source behind reviewDetail |
| `gap_evidence` | source behind observedResponseGap |
