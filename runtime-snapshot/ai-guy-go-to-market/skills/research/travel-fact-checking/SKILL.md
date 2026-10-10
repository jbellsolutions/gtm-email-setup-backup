---
name: travel-fact-checking
description: "Use for travel claim verification."
version: 1.0.0
tags: [research, fact-checking, travel, grounded-citations]
category: research
---

# Travel Fact-Checking

## When to use
Use when reviewing travel submissions or itineraries involving hotels, rentals, parking, attractions, prices, amenities, contact details, dates, or suspicious/unmatched references.

## Workflow
1. Break every submission into atomic claims: existence, exact address, phone/email, amenity, whether the amenity is free, walking distance, price, inventory, date-specific availability, discount code, and relevance to the table.
2. Search the exact property/provider name and open the official source first. Capture the exact URL and wording that supports or fails to support the claim.
3. Cross-check important claims with a major booking platform, tourism directory, airport/provider listing, or council source. Do not treat a search-result snippet alone as proof.
4. Use only three statuses: **Confirmed**, **Incorrect**, or **Unverifiable**. Confirm only when the source directly supports the precise wording.
5. Apply strict amenity rules: generic “Internet,” “wireless,” or “parking” does not prove free Wi-Fi or free parking. Require “free,” “complimentary,” “included,” or equivalent explicit wording.
6. Treat prices and inventory as dynamic. A room/vehicle category may exist while a quoted amount or availability for exact dates remains Unverifiable. Never upgrade a price because it “sounds plausible.”
7. For distances, distinguish an official stated walking time from vague marketing such as “central” or “convenient.” Mark short walking distance Unverifiable unless a source gives a walk time/distance or reliable map evidence.
8. For promo codes and booking instructions, require evidence on the official provider site or a current valid booking flow. An input box for promo codes does not validate a particular code.
9. Check anomalies independently. A footer name may refer to a real place yet still be an incorrect/unmatched leftover if it does not occur in the tables being reviewed.
10. Present a compact table: Claim | Status | Source URL | One-line note. End with a short list of wrong, unsupported, or apparently copied details.

## Evidence and citation discipline
Use the `grounded-citations` procedure when available: register source URLs at retrieval time, cite every externally sourced claim, and retain exact supporting wording for high-stakes verification. If a site is blocked or a live booking flow cannot be accessed, say so and mark only the affected claim Unverifiable; do not generalize the access problem into a claim that the property or service does not exist.

## Pitfalls
- Do not call a price “Confirmed” from an old, generic, or undated listing.
- Do not call free Wi-Fi or free parking Confirmed without explicit free/included language.
- Do not conflate “property exists” with “the submitted address, price, amenity, or distance is correct.”
- Do not mark a name as fabricated solely because search access is incomplete; use Unverifiable and explain the evidence gap.
- Do not use a broad council claim to validate every street or car park; parking rules vary by location and time limit.

## References
- `references/travel-verification-checklist.md` contains the reusable claim matrix and status rules.
