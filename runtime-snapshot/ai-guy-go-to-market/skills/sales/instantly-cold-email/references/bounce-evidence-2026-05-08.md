# Bounce Evidence — Med-Spa Campaign (May 8, 2026)

Campaign 3287518 (ai-operator-10hr-niche), 500 leads processed, 20 bounces (4.0%).

All leads were PipelineLabs "verified" — `emailStatus: "verified"` in scrape output. No additional verification was run before Instantly upload.

## Bounce Breakdown

| Lead | Email | Bounce Type |
|---|---|---|
| Ryan Bloch | ryan@skinneymedspa.com | Address not found (550 5.1.1) |
| Melissa Dickinson | melissadickinson@feelsynergy.com | Address not found (550 5.1.1) |
| Ashley Feasel | ashley@bhrcenter.com | Address not found (550 5.1.1) |
| Lindsey Bridges | lindsey@resalonandmedspa.com | Address not found (550 5.1.1) |
| Jasmin Taliadouros | jtaliadouros@medicalaestheticsne.com | Message blocked |
| Nikki Browning | nikki@belleviemedspa.com | Address not found |
| Stuart Carson | scarson@dermskin.com | (bounce, not yet inspected) |
| Lagrasta Marie | marie@wkfc.com | (bounce, not yet inspected) |
| Caitlin Soriano | caitlin@projectedgrowthconsulting.com | (bounce, not yet inspected) |
| Candace Thrash | jfox@perfectphones.net | (bounce, not yet inspected) |
| Christy Agren | dragren@chiropracticlifecenter.com | (bounce, not yet inspected) |
| Alexandra Beepat | abeepat@lotuswellnesscenter.net | (bounce, not yet inspected) |
| Bethany Anderson | bethany@illumelaserspa.com | (bounce, not yet inspected) |
| Genevieve Tripp | gtripp@cherrycreekwellnesscenter.com | (bounce, not yet inspected) |
| Charity Hagains | charity.hagains@noyau.com | (bounce, not yet inspected) |
| Michelle Whittaker | michelle.whittaker@dvidaclinic.net | (bounce, not yet inspected) |
| Mary Sather | mary.sather@healthybaldwin.org | (bounce, not yet inspected) |
| Rick Kidwell | rkidwell@cayugamed.org | (bounce, not yet inspected) |
| Bob Napack | bnapack@watg.com | (bounce, not yet inspected) |
| Julie Pulcipher | jpulcipher@grmedcenter.com | (bounce, not yet inspected) |

## Root Cause

PipelineLabs `emailStatus: "verified"` means the email was verified at scrape time — but:
1. Mailboxes get deactivated after scrape
2. Some domains use catch-all MX (accepts all mail, then silently drops or bounces later)
3. Some recipient servers block based on sender reputation, not address validity

## Remediation

Run Apify email verifier (`xlWThR6pfc9ka55eH`) on ALL leads before Instantly upload. Discard score <40, flag score 40-69. Expected reduction: 15-18 of 20 bounces caught pre-upload.

## Instantly Status Mapping After Bounce

- `BLOCKED`: Instantly auto-detected the bounce and stopped the sequence
- `COMPLETED`: Sequence finished (but for these leads, it means Instantly didn't detect the bounce and kept trying — Jasmin got email #1 on both May 6 AND May 7 from different inboxes)
