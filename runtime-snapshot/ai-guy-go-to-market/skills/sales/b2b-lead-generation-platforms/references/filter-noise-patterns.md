# Noise Filter Patterns

Known false positives encountered during Meta Ad Library extraction, organized by vertical.

## Men's Health ("TRT")

False positives from "TRT" alone:
- TRT World Citizen — Turkish media (trtworldcitizen)
- TRT ÇMK — Turkish children's media (trtcocukmedyasi)
- TRT Afrika / TRT Afrika Hausa — Turkish media in Africa (trtafrika, trtafrikaHA)
- TRT Belgesel — Turkish documentary awards (trtuluslararasibelgeselodulleri)
- Trtl — travel pillow company (trtl)
- TRP Parts — auto parts (61574601466593)
- Trtvault — unrelated

Fix: Use "TRT clinic" or "testosterone replacement clinic" instead of bare "TRT".

Filter pattern (JS):
```javascript
if (name.match(/TRT (World|ÇMK|Afrika|Belgesel|method)/i)) return;
if (page_id.match(/trtworld|trtcocuk|trtafrika|trtmethod|trtl|trtvault/i)) return;
```

## Med Spas ("botox")

False positives from "botox" alone:
- International clinics (Korea, Vietnam, India, Middle East)
- Cosmetic product brands (not clinics)
- Individual practitioners (not businesses)
- Botox Bar Italia — bar, not med spa

Fix: Use "botox clinic" or "medspa" instead of bare "botox".

## Weight Loss ("semaglutide")

False positives:
- Pharma news/education sites
- Law firms advertising semaglutide lawsuits
- Supplement companies (not clinics)

Fix: Use "semaglutide clinic" or "weight loss clinic".

## Behavioral Health ("drug rehab")

False positives from "drug rehab":
- Political ads mentioning drug policy (Donald Trump, PragerU)
- News outlets covering addiction (The Daily Show, Yahoo)
- Scientology Network — unrelated
- General health products (Lifepro, Silver Fern)

Fix: Use "addiction treatment center" or "drug rehab center" for cleaner results.

## Home Improvement ("kitchen remodel")

False positives:
- Realtors (mention remodeling in listings)
- AI apps (Remodel AI, AI Translate)
- Marketplace listings (not advertisers)
- Lifestyle bloggers (not contractors)

Fix: Use "kitchen remodel contractor", "bath remodel contractor", or "window replacement company".

## General Noise Filter (Apply to All Verticals)

Always exclude:
- l.facebook.com redirect links
- facebook.com/help, /policies, /privacy, /language pages
- "Log in", "confirm your age", "English (US)", "Cookies", "Terms", "FAQ"
- "See ad details", "See summary details", "Open Dropdown"
- "INSTAGRAM.COM", "Visit Instagram Profile"
- "URLGENI.US", "Shop now", "Learn More", "Apply now"
- profile.php links (id=... format)
- marketplace links