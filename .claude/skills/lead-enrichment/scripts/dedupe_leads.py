#!/usr/bin/env python3
"""Split a fresh scrape into net-new rows and rows already enriched before.

Re-researching a company costs about two web searches and buys nothing, so this
runs before enrichment, not after. Matching is on email first (exact identity)
and then companyDomain, which catches the same company arriving under a
different contact.
"""
import argparse, csv, sys


def load_seen(paths):
    emails, domains = set(), set()
    for p in paths:
        for r in csv.DictReader(open(p)):
            if r.get("email"):
                emails.add(r["email"].strip().lower())
            for key in ("companyDomain", "domain"):
                if r.get(key):
                    domains.add(r[key].strip().lower())
                    break
    return emails, domains


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fresh", help="newly scraped CSV")
    ap.add_argument("--against", nargs="+", required=True, help="previously enriched CSVs")
    ap.add_argument("--out", required=True, help="where to write the net-new rows")
    a = ap.parse_args()

    emails, domains = load_seen(a.against)
    rows = list(csv.DictReader(open(a.fresh)))
    if not rows:
        sys.exit("fresh file has no rows")

    new, dup_email, dup_domain = [], [], []
    for r in rows:
        em = (r.get("email") or "").strip().lower()
        dom = (r.get("companyDomain") or "").strip().lower()
        if em and em in emails:
            dup_email.append(r)
        elif dom and dom in domains:
            dup_domain.append(r)
        else:
            new.append(r)

    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(new)

    print(f"{len(rows)} scraped")
    print(f"  {len(dup_email)} already seen (same contact)")
    print(f"  {len(dup_domain)} already seen (same company, new contact)")
    print(f"  {len(new)} net new -> {a.out}")
    if new and len(new) / len(rows) < 0.5:
        print("\nover half the scrape is already enriched; widening the filters "
              "reset the progress cursor, or the pool is close to exhausted")


if __name__ == "__main__":
    main()
