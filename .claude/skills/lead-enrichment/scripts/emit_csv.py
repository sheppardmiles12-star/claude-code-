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
           "hold_reason", "reviewDetail", "painPointOpener", "observedResponseGap"]

VARIABLE_COLS = ["businessName", "reviewDetail", "painPointOpener", "observedResponseGap"]
DASHES = ["—", "–"]


def emit(rows, out_path):
    with open(out_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: (r.get(c) or "") for c in COLUMNS})
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
            if variant == "standard":
                if not r.get("reviewDetail"):
                    problems.append(f"{who}: standard variant but reviewDetail is empty")
                if r.get("painPointOpener"):
                    problems.append(f"{who}: standard variant should not set painPointOpener")
            elif variant == "negative_review":
                if not r.get("painPointOpener"):
                    problems.append(f"{who}: negative_review variant but painPointOpener is empty")
                if r.get("reviewDetail"):
                    problems.append(f"{who}: negative_review variant should not set reviewDetail")
            else:
                problems.append(f"{who}: send_ready but email_variant is '{variant}'")
        elif r.get("send_ready") == "no":
            if not r.get("hold_reason"):
                problems.append(f"{who}: held with no hold_reason")
            if r.get("reviewDetail") or r.get("painPointOpener") or r.get("observedResponseGap"):
                problems.append(f"{who}: held but still carries variable text")
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
