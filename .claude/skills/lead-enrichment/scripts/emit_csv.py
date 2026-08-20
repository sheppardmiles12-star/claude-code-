#!/usr/bin/env python3
"""Emit and validate the trimmed send-ready lead CSV.

Two modes:
  emit      build the CSV from a JSON list of enriched row dicts
  validate  check an existing CSV against the rules in SKILL.md

The column order is fixed because the user's sending tool maps against it.
"""
import argparse, collections, csv, json, re, sys

COLUMNS = ["firstName", "lastName", "email", "phone", "companyName", "businessName",
           "companySize", "annualRevenue", "companyCity", "companyState", "companyCountry",
           "personCity", "personState", "personCountry", "email_variant", "send_ready",
           "hold_reason", "reviewDetail", "observedResponseGap",
           "subject", "emailBody"]

VARIABLE_COLS = ["businessName", "reviewDetail", "observedResponseGap"]
DASHES = ["\u2014", "\u2013"]

# The body is rendered here rather than written by hand so the CSV can never
# drift from the template. Change the wording in one place and every row follows.
MIDDLE = (
    "\n\ni run a b2b automation agency where i catch the calls/leads that come in after "
    "hours or via form so they dont just sit there til someone gets around to it. figured "
    "worth a shot since {observedResponseGap}.\n\nive done my homework on you guys and "
    "believe i can help out {businessName}. are you open to finding out more? if so it'd "
    "take no more than 15 min over the phone to break it down for you."
)
# Both variants open on reviewDetail; the difference is the framing around it.
# Standard points at a compliment, negative points at a fixable gap, so the
# greeting runs inline and the signoff sits off on its own.
STANDARD = ("heyy {firstName}, \n\nsaw {businessName} recent review where {reviewDetail}, "
            "and wanted to say hi." + MIDDLE + "\nmiles")
NEGATIVE = ("heyy {firstName}, read through {businessName} reviews {reviewDetail}."
            + MIDDLE + "\n\nmiles")


def render(row):
    """Return (subject, body) for a row, or ("", "") when the row is held."""
    if row.get("send_ready") != "yes":
        return "", ""
    tpl = NEGATIVE if row.get("email_variant") == "negative_review" else STANDARD
    return row.get("firstName", ""), tpl.format(**{k: row.get(k, "") for k in
        ("firstName", "businessName", "reviewDetail", "observedResponseGap")})


def emit(rows, out_path):
    with open(out_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            out = {c: (r.get(c) or "") for c in COLUMNS}
            out["subject"], out["emailBody"] = render(r)
            w.writerow(out)
    return out_path


def validate(path):
    rows = list(csv.DictReader(open(path)))
    problems = []

    if not rows:
        return ["file has no data rows"]
    if list(rows[0].keys()) != COLUMNS:
        problems.append("column set/order does not match the required schema")

    for i, r in enumerate(rows, start=2):
        who = r.get("email") or f"row {i}"

        for c in VARIABLE_COLS:
            for d in DASHES:
                if d in (r.get(c) or ""):
                    problems.append(f"{who}: {c} contains a dash character")

        if r.get("send_ready") == "yes":
            if not r.get("observedResponseGap"):
                problems.append(f"{who}: send_ready but observedResponseGap is empty")
            if not r.get("businessName"):
                problems.append(f"{who}: send_ready but businessName is empty")
            variant = r.get("email_variant")
            if variant in ("standard", "negative_review"):
                if not r.get("reviewDetail"):
                    problems.append(f"{who}: {variant} variant but reviewDetail is empty")
            else:
                problems.append(f"{who}: send_ready but email_variant is '{variant}'")

            body = r.get("emailBody") or ""
            if not body:
                problems.append(f"{who}: send_ready but emailBody is empty")
            if "{" in body or "}" in body:
                problems.append(f"{who}: emailBody has an unreplaced placeholder")
            for d in DASHES:
                if d in body:
                    problems.append(f"{who}: emailBody contains a dash character")
            if r.get("subject") != r.get("firstName"):
                problems.append(f"{who}: subject should be the contact first name")
        elif r.get("send_ready") == "no":
            if not r.get("hold_reason"):
                problems.append(f"{who}: held with no hold_reason")
            if r.get("reviewDetail") or r.get("observedResponseGap"):
                problems.append(f"{who}: held but still carries variable text")
            if r.get("emailBody") or r.get("subject"):
                problems.append(f"{who}: held but still carries a rendered email")
        else:
            problems.append(f"{who}: send_ready must be yes or no")

    # batch-level sameyness: repeated opening phrasing reads as a template
    for col in ("reviewDetail", "observedResponseGap"):
        opens = [" ".join((r.get(col) or "").split()[:3]) for r in rows if r.get(col)]
        for phrase, n in collections.Counter(opens).items():
            if n > 2:
                problems.append(f"batch: {col} opens with '{phrase}' {n} times, vary it")

    ready = sum(1 for r in rows if r.get("send_ready") == "yes")
    print(f"{len(rows)} rows | {ready} send-ready | {len(rows)-ready} held")
    return problems


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--rows", help="JSON file of enriched row dicts (emit mode)")
    p.add_argument("--validate", action="store_true")
    a = p.parse_args()

    if a.validate:
        problems = validate(a.path)
    else:
        if not a.rows:
            sys.exit("emit mode needs --rows <file.json>")
        emit(json.load(open(a.rows)), a.path)
        problems = validate(a.path)

    if problems:
        print("\nFAILED:")
        for x in problems:
            print("  -", x)
        sys.exit(1)
    print("validation passed")


if __name__ == "__main__":
    main()
