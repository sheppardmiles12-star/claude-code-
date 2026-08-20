#!/usr/bin/env python3
"""Enrich the Apollo lead export with AI merge variables for the cold-email template."""
import csv, sys

NEW_COLS = ["businessName", "email_variant", "send_ready", "hold_reason", "subject",
            "reviewDetail", "painPointOpener", "observedResponseGap",
            "review_evidence", "gap_evidence"]

# keyed by the row's email address (unique per row in this export)
E = {}

def ready(em, biz, review, gap, rev_src, gap_src, variant="standard", opener=""):
    E[em] = dict(businessName=biz, email_variant=variant, send_ready="yes", hold_reason="",
                 reviewDetail=review, painPointOpener=opener, observedResponseGap=gap,
                 review_evidence=rev_src, gap_evidence=gap_src)

def hold(em, biz, reason):
    E[em] = dict(businessName=biz, email_variant="", send_ready="no", hold_reason=reason,
                 reviewDetail="", painPointOpener="", observedResponseGap="",
                 review_evidence="", gap_evidence="")

# ---------------- send-ready: standard variant ----------------
ready("mark@empireroofcoatings.com", "Empire Roof Coatings",
  "someone said they'd called a bunch of companies for a bid and you were the first one to actually get back to them",
  "the only ways in are a phone number, a gmail address and the form on your contact page, so a building manager who spots a leak sunday morning has nowhere to land",
  "Facebook/Angi review: customer called numerous companies for bids on a leaking roof with none getting back to them in a timely manner until Empire; also punctual on show times",
  "empireroofcoatings.com/contact offers call 509-230-7262 or fill out the form; public email is a gmail address; posted hours Mon-Fri 8-5, Sat 10-3, Sun closed; no live chat, text line or booking found")

ready("amber@sqiinc.com", "SQI",
  "whoever wrote it said you were easy to communicate with and fast with it",
  "you advertise 24/7 emergency service but the office itself runs 7 to 5 on weekdays and goes dark all weekend, so the two dont quite line up",
  "sqiroofing.com/reviews: \"SQI was amazing and easy to communicate with. They were fast and the roof looks awesome.\"",
  "sqiroofing.com advertises 24/7 emergency service and an emergency line 425.348.ROOF; posted office hours Mon-Fri 7:00am-5:00pm, Sat/Sun closed")

ready("connor@valentineroof.com", "Valentine Roofing",
  "a homeowner said your foreman updated them every single day, weekends included",
  "your emergency page promises 24/7 but the thing actually catching a 2am call is a voicemail box that somebody has to listen to before anyone calls back",
  "GuildQuality review (Jan 2025): very communicative, updated the customer every single day even on weekends, foreman flagged rain delays by 8:00am",
  "valentineroof.com emergency page advertises 24/7 emergency roof repair and states the response team monitors voicemail 24/7 for callback; posted office hours Mon-Thu 8-5, Fri 8-4, closed weekends")

ready("steven@valentineroof.com", "Valentine Roofing",
  "one review mentioned your foreman was flagging weather delays by 8 in the morning so nobody was left guessing",
  "theres a 24/7 emergency promise on the site and a voicemail box sitting behind it, which is a lot of weight to put on whoever checks it first in the morning",
  "GuildQuality review (Jan 2025): foreman communicated rain delays by 8:00 in the morning, customer updated every single day including weekends",
  "valentineroof.com emergency page advertises 24/7 emergency roof repair and states the response team monitors voicemail 24/7 for callback; posted office hours Mon-Thu 8-5, Fri 8-4, closed weekends")

ready("c.hathaway@yourguardianroof.com", "Guardian Roofing",
  "you got called out for coming back quickly whenever something was raised",
  "sundays youre closed outright, and the web form doesnt care what day it is when somebody fills it out",
  "Yelp/HomeAdvisor reviews: customers praise timely responses to concerns and a smooth process from the first phone call to final inspection",
  "Posted hours Mon-Fri 7:00am-7:00pm, Sat 8:00am-4:00pm, closed Sunday; site takes web form submissions with no chat or text line")

ready("salvador@anytimeroofingco.com", "Anytime Roofing",
  "a customer said you walked them through the whole thing and called them back the next day",
  "your site tells people to expect 24 to 48 hours on an estimate request, and with the office closed saturday and sunday a friday afternoon one is really waiting til monday",
  "HomeAdvisor review: owner Salvador Santos explained everything clearly, answered questions, and called the next day",
  "anytimeroofingco.com contact page states a 24-48 hour response window on estimate requests; Yelp posts Mon-Fri 8-5, closed Sat/Sun, no emergency service; contact = phone, gmail, web form")

ready("david@legitroofing.com", "Legit Roofing",
  "the words used were that you communicated effectively the whole way through",
  "youre open late most days and even saturdays, which makes sunday the odd one out, and a sunday form fill still waits til monday morning for somebody to see it",
  "GuildQuality/HomeAdvisor reviews: \"Legit Roofing communicated with me effectively\" and \"good communication & overall quality of work\"",
  "Posted hours Mon-Fri 9:00am-7:30pm, Sat 9:00am-5:00pm, closed Sunday; site uses gravity_forms web form (per technology stack) with no chat or text line")

ready("nathan@monorooftop.com", "Mono Rooftop Solutions",
  "they described you as fast and efficient and said you followed through on what you committed to",
  "the office runs 8 to 4 and shuts weekends, and the after hours number is a separate line someone has to already know to call",
  "Facebook/BuildZoom reviews: affordable, fast, efficient, left no mess, great integrity and follow-through on commitments",
  "Posted hours Mon-Fri 8:00am-4:00pm, Sat/Sun closed; a separate after-hours number (206) 255-7259 appears on directory listings rather than as a primary site contact")

ready("derrick@unitedroofs.com", "United Roofing Solutions",
  "more than one reviewer singled out how quickly you respond",
  "the 24 hour emergency line is a real promise to keep, and with the office running 8 to 4:30 on weekdays only theres a stretch where keeping it depends on somebody happening to look at their phone",
  "Yelp/HomeAdvisor/BBB reviews across platforms highlight responsiveness and customer service; A+ BBB rating",
  "unitedroofs.com advertises 24 hour emergency roof patch assistance and same-day response on active leaks; posted office hours Mon-Fri 8:00am-4:30pm, Sat/Sun closed")

ready("sam@stateroofing.com", "State Roofing",
  "somebody wrote that you were constantly communicating with them the whole way through the job",
  "you tell people youre there 24/7 for emergencies while the posted hours stop at 6:30, and the gap between those two is exactly where a panicked call lands",
  "Birdeye reviews (4.5 stars, 253 reviews): \"great to communicate with and very no-pressure\", \"totally professional, constantly communicating with us about the job\"",
  "State Roofing & Exteriors advertises 24/7 availability for emergencies; posted business hours 7:30am-6:30pm")

ready("bill.sullivan@cornerstoneroofing.com", "Cornerstone Roofing",
  "the follow up got described as immediate and they said they were kept in the loop start to finish",
  "monday to friday 8 to 5 is the whole window, so anything that shows up saturday morning has two full days before anyone opens it",
  "GuildQuality/Houzz reviews: communication was clear, follow-up was immediate, project coordination completely seamless, kept fully informed at all times",
  "Posted hours Mon-Fri 8:00am-5:00pm, Sat/Sun closed; contact is phone plus info@ email and a web form")

ready("kylek@jameskingroofing.com", "James King Roofing",
  "your service team got singled out for how responsive they were when something needed solving",
  "commercial leaks dont keep office hours and yours stop at 4, so a facilities manager finding water on a saturday is waiting on monday before anyone even reads it",
  "Google reviews (3.1 stars, 25 reviews): positive feedback highlights responsiveness and problem-solving from the service team",
  "Posted hours Mon-Fri 7:00am-4:00pm; contact is phone (425) 374-7955 and service@ email, no after-hours mechanism listed")

ready("brendan@jobinroofing.com", "Jobin Roofing",
  "somebody compared your bid and your communication to the other companies they had talked to and yours came out ahead",
  "theres no hours posted anywhere and the way in is a form on your site, so someone filling it out at 9pm has no idea whether that means tonight or thursday",
  "jobinroofing.com/client-reviews and Porch: 150+ five-star reviews, \"communication was excellent and the crew was very professional onsite\", one customer impressed by how thorough the bid and communication were versus other companies",
  "No business hours listed on any directory (explicitly noted as not listed); contact is a PO Box plus a website request-an-estimate form")

ready("michael@larryhaight.com", "Larry Haight's",
  "reviewers keep mentioning how quickly you come back to them when something comes up",
  "the posted hours are plain weekday business hours, and roof problems have a habit of announcing themselves at 6pm on a saturday",
  "Angi (4.8 stars) and Checkbook (86% superior): customers consistently praise excellent communication, responsiveness and quick response in solving problems",
  "Posted hours begin Mon-Wed 8AM-5PM on directory listings, weekday business hours only; no 24/7 or emergency claim found")

ready("larry@larryhaight.com", "Larry Haight's",
  "the phrase that came up was responsive and willing to explain things properly",
  "everything on your listing points to weekday office hours, so evenings and weekends are running on whoever happens to check",
  "Angi (4.8 stars) and Checkbook: team described as responsive and knowledgeable, providing thorough explanations of services",
  "Posted hours begin Mon-Wed 8AM-5PM on directory listings, weekday business hours only; no 24/7 or emergency claim found")

ready("don.vose@legendsco.com", "Legends Roofing",
  "one review said they got a great response from you when they called and that you kept them informed after",
  "great response when somebody calls is the hard part and youve clearly got that, the easier miss is the call that comes in at 4:30 once the line has already gone quiet",
  "Angi/Nextdoor/Checkbook reviews: \"great response from company when I called\", \"responsive to needs, kept me informed\", \"very responsive\"",
  "Posted hours 8:00am-4:00pm; contact is phone (253) 548-3197, no after-hours mechanism listed")

ready("dan@northcreekroofing.com", "North Creek Roofing",
  "your office, sales and production teams all got credit for communicating every step of the way",
  "the office is 8 to 5 and dark on weekends, so the saturday callers are choosing between waiting til monday and calling the next name on the list",
  "GuildQuality/Yelp (4.9 stars, 518 reviews): \"great communication, on time, efficient crew\", \"the North Creek office, sales, and production teams communicated every step of the way\", described as fair, honest, responsive",
  "Posted hours Mon-Fri 8:00AM-5:00PM, Sat/Sun closed; contact is phone plus web form")

ready("jackie.mears@mearsroofs.com", "Mears Roofing",
  "quick to respond and quick to follow up was how one customer put it",
  "most people only get round to dealing with the roof once theyre home from work, which is right about when your 7:30 to 4 day has already ended",
  "mearsroofs.com/reviews and Yelp (142 reviews): praised for transparent communication discussed upfront, \"very quick to respond and follow up with any questions/concerns\"",
  "Posted hours Mon-Fri 7:30am-4:00pm, closed weekends; contact is phone and web form")

# ---------------- send-ready: negative-review variant ----------------
ready("dave@elementsmartroofing.com", "Element Smart Roofing",
  "", "your public contact is a gmail address, and between that and a sunday with nobody in the office its easy for something to land and just sit",
  "HomeAdvisor/Angi: no communication-specific positive review found; a review describes promised follow-up work not being returned to after the initial visit",
  "Posted hours Mon-Fri 7AM-5PM, Sat 12:00pm-5:00pm, closed Sunday; public contact email is ELEMENTSMARTROOFING@GMAIL.COM",
  variant="negative_review",
  opener="read through your reviews and it looks like the follow up after that first visit is where things occasionally slip, figured that was worth a mention")

ready("jon@pacificbuildingenvelope.com", "Pacific Building Envelope",
  "", "you describe yourselves as handling the communication load from tenants, owners and property managers, and 8 to 5 on a phone line is a narrow pipe for all of that",
  "BBB: B- rating driven by failure to respond to 1 complaint; no customer reviews on BuildZoom or Yellow Pages",
  "Company description emphasises working closely with HOAs and property owners and communicating with residents; posted hours 8:00am-5:00pm; contact is phone (425) 512-8455",
  variant="negative_review",
  opener="your bbb profile has a complaint sitting on it with no reply attached, and that usually says process rather than anyone not caring")

ready("tim@hytechroofing.com", "Hytech Roofing",
  "", "your site promises clear consistent communication throughout, and youre open six days, which just leaves the seventh and everything that lands after hours",
  "Yelp: reviewer reported significant delays getting an estimate and no response to follow-up calls and emails; company later called to apologise and attributed it to a systems changeover",
  "hytechroofing.com states they communicate clearly and consistently throughout the project, proactively addressing complications; listed as available Monday through Saturday",
  variant="negative_review",
  opener="came across a review about an estimate that took a while to come back, and it read a lot more like a system gap than a people one")

# ---------------- held rows ----------------
hold("richlopez@affordableroofcare.com", "Affordable Roof Care",
  "facebook lists the business as permanently closed; verify it is still trading before any send")
hold("kade@holtzlanderroofing.com", "Holtzlander Roofing and Services",
  "usable review exists (12-year customer: professional, upfront, punctual) but no posted hours or contact-mechanism evidence found, so observedResponseGap cannot be filled without inventing one")
hold("jim@westernmetalproducts.com", "Western Metal Products",
  "no customer reviews and no posted hours found; architectural sheet metal fabricator rather than a contractor taking inbound service calls")
hold("johnherzog@america1stroofing.com", "America 1st Roofing & Builders",
  "2.6 star average and the complaints are about workmanship, which the rules exclude; no communication or response-speed review available either way")
hold("richard@soundbuildingsupply.com", "Sound Building Supply",
  "strong gap available (their own line about anyone who picks up the phone being able to help, plus a 24-hour custom order claim) but no review speaks to communication or response speed, only service and warranty generally")
hold("jim@tedricksroofing.com", "Tedrick's Roofing",
  "responsiveness complaints present (customers describing them as very slow) but no posted hours or contact mechanism found to pair with them for observedResponseGap")
hold("parq@impactroof.com", "Impact Roofing",
  "sheet places them in Shoreline WA but the company description and every search result point to Tulsa and Oklahoma City; no WA presence, reviews or hours found")
hold("mason@impactroofing.solutions", "Impact Roofing",
  "same data mismatch as the impactroof.com row: Shoreline WA in the sheet, Tulsa/Oklahoma City everywhere else; email domain impactroofing.solutions also differs from the listed companyDomain")
hold("ahronb@cobraresults.com", "Cobra BEC",
  "no customer reviews found, only employee reviews; Cobra BEC also appears to now trade as Flynn BEC under Flynn Group, so verify the entity before any send")
hold("ericd@cobraresults.com", "Cobra BEC",
  "same as the other Cobra row: no customer reviews, and a likely rebrand to Flynn BEC under Flynn Group")
hold("roger@macphersonconstruction.com", "MacPherson Construction & Design",
  "5.0 rated but no communication or response-speed review found; custom home builder working from design through build rather than a business fielding urgent inbound calls")
hold("patb@sidepro.com", "Side-Pro",
  "the review found praises workmanship and general customer service together, nothing specific to communication or response speed, and craft praise is excluded by the rules")
hold("teri@smartchoiceir.com", "Smart Choice Insulation & Roofing",
  "no reviews on any platform and no posted hours found")
hold("dave@deamor.com", "DeaMor Associates",
  "no customer reviews found and BBB has insufficient information to issue a rating")
hold("ted@jorve.com", "Jorve Roofing",
  "yelp lists the business as closed; verify operating status before any send")
hold("john@tristate.pro", "Tristate Roofing",
  "usable communication review available (communication from start to finish was very professional) but only an opening time of 8:00am is posted, with no closing time or weekend hours found to build the gap on")
hold("jenn@lifetime-exteriors.net", "Lifetime Exteriors",
  "strong communication reviews available (very responsive, communicates well and often) but no posted hours and no capture-mechanism evidence found for observedResponseGap")
hold("krisd@lifetime-exteriors.net", "Lifetime Exteriors",
  "same as the other Lifetime Exteriors row: good review material, no hours or contact-mechanism evidence to pair with it")
hold("morgan@hanleyroofing.com", "Hanley Construction",
  "reviews praise professionalism and workmanship, nothing specific to communication or response speed")
hold("brett@roofingprosco.com", "Roofing Pros",
  "no customer reviews found, and the sheet domain roofingprosusa.com does not match the roofingproswa.com listing that search resolves to; email domain roofingprosco.com is a third variant")
hold("don.prociw@rainier-view.com", "Rainier View Construction & Roofing",
  "the communication mentions in the reviews are the negative ones and the positive reviews are about courtesy and professionalism; no posted hours or contact mechanism found to pair with a negative-variant opener")
hold("sheila@leewens.com", "Leewens Corporation",
  "no customer reviews found on any platform (0 reviews on Facebook, not BBB accredited)")
hold("pat@leewens.com", "Leewens Corporation",
  "same as the other Leewens row: no customer reviews found on any platform")
hold("michael.hammes@ramconstruction-wa.com", "RAM Construction General Contractors",
  "row data is internally inconsistent: companyName reads hope contrs shreveport inc, the email domain is ramconstruction-wa.com, and firstName Ronald Pyles does not match the michael.hammes mailbox, so the firstName merge would address the wrong person")
hold("scott@buildingsciencethermography.com", "Scott Wood Associates",
  "building science and thermography consultancy rather than a contractor fielding inbound service calls; out of ICP, not researched")
hold("bryan@cascadianland.works", "Cascadian Landworks",
  "landscaping rather than roofing or an inbound-service trade; out of ICP, not researched")
hold("heathtalbert@talbertconstruction.com", "Talbert Construction",
  "search resolves almost entirely to a same-named company in Waco, Texas; no reviews or hours confirmed for the Anacortes WA entity")
hold("brenda@pacificprideroofing.com", "Pacific Pride Roofing",
  "good communication reviews available but no posted hours found for the gap, and firstName Lonnie does not match the brenda@ mailbox, which would break the firstName greeting and subject")
hold("creid@insulfoam.com", "Insulfoam",
  "EPS manufacturer rather than an inbound-service contractor, and the contact's title places them at a Mead, Nebraska facility rather than the Puyallup WA address in the sheet")
hold("eric@wehoneydo.com", "We Honey Do",
  "the responsiveness signal is in the negative reviews (contractors arriving late) but no posted hours or contact mechanism found to pair with it")
hold("ewinter@gstarc.com", "Gold Star Construction",
  "no reviews on any platform (0 on Facebook, none on Yellow Pages); custom home builder rather than an inbound-service roofing business")
hold("carl@wrayscontracting.com", "Wray's Contracting",
  "no reviews found and the general contractor license shows as expired; verify the business is still trading")
hold("hans@foreverlawnbellevue.com", "ForeverLawn Bellevue",
  "artificial turf installer rather than roofing or an urgent-response trade; out of ICP, not researched")
hold("dhornsby@id-engr.com", "Integrated Design Engineers",
  "engineering consultancy rather than a contractor fielding inbound service calls; out of ICP, not researched")

# ---------------- write ----------------
src, dst = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src)))
fields = list(rows[0].keys()) + NEW_COLS
missing = []
with open(dst, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in rows:
        v = E.get(r["email"])
        if v is None:
            missing.append(r["email"]); v = {}
        r.update({c: v.get(c, "") for c in NEW_COLS})
        r["subject"] = r["firstName"] if v.get("send_ready") == "yes" else ""
        w.writerow(r)

print("rows written:", len(rows))
print("unmapped:", missing or "none")
print("send_ready yes:", sum(1 for r in rows if r["send_ready"] == "yes"))
print("negative_review:", sum(1 for r in rows if r["email_variant"] == "negative_review"))
