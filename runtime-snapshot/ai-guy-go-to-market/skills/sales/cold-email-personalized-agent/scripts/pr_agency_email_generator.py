#!/usr/bin/env python3
"""
PR Agency Cold Email Generator — SpeakerAgent-First Framework Engine.
Processes verified PR agency leads (from ListKit/PipelineLabs), selects framework 
via scoring-based matching biased to SpeakerAgent (#7), generates 50-100 word 
personalized cold emails per the v3 frameworks doc.

Input: CSV with columns Domain, Name, Description, email, City, State, etc.
Output: CSV with first_name, email, company_name, email_subject, email_body, framework, etc.

Usage:
    python3 pr_agency_email_generator.py input.csv output.csv [start] [count]
"""
import csv, json, re, random, sys
from pathlib import Path

# ─── FRAMEWORKS ───
FRAMEWORKS = {
    "7": {"name": "White-Label SpeakerAgent — No Cap Pitching",
          "subjects": ["no cap", "podcast engine", "your bookings"],
          "template": """{greeting} {first_name},

Saw {signal_detail}.

Honest ceiling on most agency podcast booking is 10–20 pitches per client per month because every pitch is hand-built. Client maxes out, then you're back to the spreadsheet.

Let me take it off your plate. I plug a growth operator in from my team running SpeakerAgent.ai as your hidden person under your brand — part-time or full-time. We architect and manage. No cap on shows pitched.

{cta}"""},
    "1": {"name": "The Podcast Service They Keep Asking For",
          "subjects": ["podcast booking", "your clients", "quick thought"],
          "template": """{greeting} {first_name},

Saw {signal_detail}.

Most PR agencies I talk to don't have a real podcast booking arm. Clients keep asking, you half-deliver, and they shop a podcast service on the side.

Let me take it off your plate. I plug a growth operator in from my team as your team's hidden person under your brand — part-time or full-time. We architect and manage the pitching engine, you stay on strategy.

{cta}"""},
    "2": {"name": "The LinkedIn Layer You Don't Run",
          "subjects": ["linkedin layer", "quick one", "your retainers"],
          "template": """{greeting} {first_name},

Noticed {signal_detail}.

Pattern I keep seeing: client signs a $2K/mo ghostwriter and trims the PR retainer to fund it.

Let me take the LinkedIn execution off your plate. I bring a growth operator in from my team as your hidden person under your brand — part-time or full-time. We architect and manage daily posting, comments, DMs. You keep the retainer line.

{cta}"""},
    "3": {"name": "Newsletter Clients Want, You Can't Build",
          "subjects": ["newsletter ask", "owned audience", "your clients"],
          "template": """{greeting} {first_name},

Saw {signal_detail}.

Most PR agencies are pitching newsletter as a deliverable but can't actually staff weekly writing and sending. Different muscle than media relations.

Let me take the weekly newsletter off your plate. I plug a growth operator in from my team as your team's hidden person under your client's name — part-time or full-time. We architect and manage the writing, design, send, and list growth. You stay client-facing.

{cta}"""},
    "4": {"name": "Journalist Reply Rates Are Done",
          "subjects": ["reply rates", "quick thought", "1-3 percent"],
          "template": """{greeting} {first_name},

Saw {signal_detail}.

Reality: reply rates are sitting at 1–3% and 3,400+ media jobs got cut this year. List rots faster than your team can clean it.

Let me take the new channels off your plate. I plug a growth operator in from my team as your hidden person under your brand — part-time or full-time. We architect and manage the LinkedIn and podcast pipeline so clients still hit earned-style numbers.

{cta}"""},
    "5": {"name": "AVE Is Dead, The New Dashboard",
          "subjects": ["the dashboard", "ai citations", "new reporting"],
          "template": """{greeting} {first_name},

Noticed {signal_detail}.

Clients are starting to ask about AI citations and LLM brand mentions now that ChatGPT and Google AI Overviews answer half their buyers' questions.

Let me take the new metrics off your plate. I plug a growth operator in from my team as your hidden person under your brand — part-time or full-time. We architect and manage the tracking, you feed it into your existing reports.

{cta}"""},
    "6": {"name": "The Fractional Comms Threat",
          "subjects": ["fractional comms", "quick heads up", "the in-house ask"],
          "template": """{greeting} {first_name},

Noticed {signal_detail}.

They usually start by managing the agency, then quietly replace pieces of scope. The hardest thing for them to actually staff in-house is a daily LinkedIn engine on the founder.

Let me take that off your plate. I plug a growth operator in from my team as your hidden person under your brand — part-time or full-time. We architect and manage.

{cta}"""},
    "8": {"name": "A Recurring Revenue Line You Don't Have",
          "subjects": ["recurring line", "retainer math", "quick idea"],
          "template": """{greeting} {first_name},

Saw {signal_detail}.

Most boutique shops I talk to see retainers renegotiated quarterly. The ones still growing tucked a recurring execution layer into every account so the monthly minimum holds.

Let me take that off your plate. I plug a growth operator in from my team as your hidden person under your brand — part-time or full-time. We architect and manage LinkedIn, newsletter, podcast booking.

{cta}"""},
    "9": {"name": "The Exec Who Hates Media Training, Loves Podcasts",
          "subjects": ["the exec pivot", "quick thought", "format shift"],
          "template": """{greeting} {first_name},

Looked at {signal_detail}.

Most PR shops retrofit those execs into press tours. The format pivot — podcast guesting plus a LinkedIn surface — is where they actually shine.

Let me take it off your plate. I plug a growth operator in from my team as your hidden person under your brand — part-time or full-time. We architect and manage every pitch, post, and DM.

{cta}"""},
    "10": {"name": "Build It Once, Run It For Every Client",
          "subjects": ["own the machine", "for your team", "quick idea"],
          "template": """{greeting} {first_name},

Saw {signal_detail}.

Most shops I talk to are rebuilding the LinkedIn + newsletter + podcast engine from scratch on every new account. Margins thin, nothing's repeatable.

Let me take the whole machine off your plate. I plug a growth operator in from my team as your team's hidden person under your brand — part-time or full-time. We architect and manage one playbook that runs across every account.

{cta}"""},
}

GREETINGS = ["Hey", "Hi", "Hello"]
CTAS = [
    "What's the typical pitch volume per client on your side?",
    "Is podcast guesting something clients have been asking about?",
    "Are clients asking about podcast and LinkedIn yet?",
    "How are you handling the podcast ask right now?",
    "Is this something that'd help your team?",
    "Curious if podcast booking is on your radar.",
    "How's the podcast pipeline looking on your end?",
    "Are your clients asking for more podcast spots than you can book?",
]

BANNED = {
    "pay", "price", "cost", "investment", "spend", "budget",
    "unlock", "10x", "synergy", "leverage", "innovative", "cutting-edge",
    "solution", "game-changer", "transform", "revolutionize", "scale your",
    "disrupt", "revolutionary", "guarantee", "roi", "affordable", "cheap",
    "expensive", "fee",
}

# Scoring-based framework selection — SpeakerAgent-first
FRAMEWORK_SCORING = {
    "7": {  # SpeakerAgent — PREFERRED, aggressive bonus
        "podcast": 6, "podcasts": 6, "speaker": 6, "speakeragent": 10,
        "booking": 4, "guest": 3, "podcast guest": 7, "podcast book": 7,
        "speaking engagement": 6, "podcast tour": 7,
        "thought leadership": 4, "executive visibility": 4, "executive comm": 4,
        "exec visib": 4, "exec comm": 3, "thought leader": 3,
        "weekly interview": 5, "weekly podcast": 6,
        "interview": 2, "media placement": 1,
        "executive": 1,
    },
    "1": {"podcast": 3, "guest": 2, "booking": 2, "interview": 1},
    "9": {"exec": 3, "ceo": 3, "founder": 4, "thought leadership": 4,
          "executive": 2, "executive visibility": 3, "exec comm": 3,
          "exec visib": 3, "thought leader": 3, "executive comm": 3},
    "2": {"linkedin": 6, "ghostwrit": 6, "thought leadership": 2, "executive comm": 3,
          "exec comm": 3, "exec visib": 3, "thought leader": 2},
    "3": {"newsletter": 6, "content market": 2, "owned audience": 3},
    "4": {"media relations": 4, "press release": 4, "earned media": 4,
          "journalist": 3, "media coverage": 3, "media placement": 2,
          "public relations": 1, "media": 1, "press": 1},
    "5": {"ai citation": 6, "ai overview": 6, "llm brand mention": 6,
          "geo": 5, "seo": 3, "citation": 5, "metric": 4, "analytics": 4,
          "reporting": 2, "measurement": 3, "data-driven": 2},
    "6": {"fractional": 7, "in-house": 2, "head of comm": 5},
    "8": {"retainer": 5, "recurring": 5, "boutique": 2},
    "10": {"hiring": 3, "playbook": 5, "standardiz": 3, "multiple client": 3},
}
MIN_SCORE = 3

NAME_MAP = {
    'chris': 'Chris', 'alex': 'Alex', 'david': 'David', 'mike': 'Mike',
    'john': 'John', 'james': 'James', 'robert': 'Robert', 'mark': 'Mark',
    'daniel': 'Daniel', 'paul': 'Paul', 'steven': 'Steven', 'andrew': 'Andrew',
    'kenneth': 'Kenneth', 'joshua': 'Joshua', 'kevin': 'Kevin', 'brian': 'Brian',
    'george': 'George', 'edward': 'Edward', 'ronald': 'Ronald', 'timothy': 'Timothy',
    'jason': 'Jason', 'jeffrey': 'Jeffrey', 'ryan': 'Ryan', 'jacob': 'Jacob',
    'gary': 'Gary', 'nicholas': 'Nicholas', 'eric': 'Eric', 'jonathan': 'Jonathan',
    'stephen': 'Stephen', 'larry': 'Larry', 'justin': 'Justin', 'scott': 'Scott',
    'brandon': 'Brandon', 'benjamin': 'Benjamin', 'samuel': 'Samuel', 'gregory': 'Gregory',
    'frank': 'Frank', 'raymond': 'Raymond', 'patrick': 'Patrick',
    'jack': 'Jack', 'dennis': 'Dennis', 'jerry': 'Jerry', 'tyler': 'Tyler',
    'aaron': 'Aaron', 'jose': 'Jose', 'adam': 'Adam', 'nathan': 'Nathan',
    'henry': 'Henry', 'douglas': 'Douglas', 'zachary': 'Zachary', 'peter': 'Peter',
    'kyle': 'Kyle', 'walter': 'Walter', 'ethan': 'Ethan', 'jeremy': 'Jeremy',
    'sarah': 'Sarah', 'jessica': 'Jessica', 'ashley': 'Ashley', 'emily': 'Emily',
    'samantha': 'Samantha', 'amanda': 'Amanda', 'elizabeth': 'Elizabeth',
    'megan': 'Megan', 'nicole': 'Nicole', 'stephanie': 'Stephanie', 'jennifer': 'Jennifer',
    'melissa': 'Melissa', 'michelle': 'Michelle', 'kimberly': 'Kimberly', 'laura': 'Laura',
    'rachel': 'Rachel', 'amber': 'Amber', 'danielle': 'Danielle', 'heather': 'Heather',
    'lauren': 'Lauren', 'rebecca': 'Rebecca', 'amy': 'Amy', 'angela': 'Angela',
    'shannon': 'Shannon', 'maria': 'Maria', 'lisa': 'Lisa',
    'tiffany': 'Tiffany', 'andrea': 'Andrea', 'mary': 'Mary', 'katherine': 'Katherine',
    'priya': 'Priya', 'naomi': 'Naomi', 'allison': 'Allison', 'jen': 'Jen',
    'marcus': 'Marcus', 'rob': 'Rob', 'sam': 'Sam', 'eli': 'Eli',
    'alissa': 'Alissa', 'elyse': 'Elyse', 'nikki': 'Nikki', 'catherine': 'Catherine',
    'shannon': 'Shannon', 'marie': 'Marie',
}

GENERICS = {'info', 'hello', 'contact', 'admin', 'sales', 'marketing',
            'pr', 'media', 'press', 'office', 'mail', 'general', 'enquiries',
            'inquiries', 'help', 'service', 'customerservice', 'accounts', 'billing',
            'business', 'company', 'corporate', 'communications', 'start', 'social',
            'support', 'team', 'ceo', 'founder', 'owner'}


def select_framework(description, company_name):
    desc_lower = (description + " " + company_name).lower()
    scores = {}
    for fid, keywords in FRAMEWORK_SCORING.items():
        score = sum(pts for kw, pts in keywords.items() if kw in desc_lower)
        if score >= MIN_SCORE:
            scores[fid] = score
    if not scores:
        return "7"
    if "7" in scores:
        if scores["7"] >= 2:
            return "7"
        best_fid = max(scores, key=scores.get)
        if scores[best_fid] >= 6 and best_fid != "7":
            return best_fid
        return "7"
    best_fid = max(scores, key=scores.get)
    return best_fid if scores[best_fid] >= 4 else "7"


def truncate_words(text, max_chars=85):
    if len(text) <= max_chars:
        return text
    result = []
    length = 0
    for w in text[:max_chars+10].split():
        if length + len(w) + (1 if result else 0) <= max_chars:
            result.append(w)
            length += len(w) + (1 if result else 0)
        else:
            break
    return ' '.join(result)


def extract_signal_detail(description, company_name, framework_id):
    desc = description
    if framework_id in ("7", "1", "9"):
        for pat in [
            r'(?:weekly\s+)?(?:podcasts?\s*(?:and|&)?\s*(?:interviews?)?)[^.,;]*',
            r'(?:thought\s+)?leadership\s+articles?[^.,;]*',
            r'speaking\s+engagement[^.,;]*',
            r'podcast\s+(?:guest|booking|tour)[^.,;]*',
            r'(?:weekly\s+)?interviews?[^.,;]*(?:podcast|thought|article)[^.,;]*',
        ]:
            m = re.search(pat, desc, re.IGNORECASE)
            result = m.group(0).strip() if m else ""
            if len(result) > 12:
                return truncate_words(result, 80)
    if framework_id in ("9", "2"):
        for pat in [
            r'thought\s+leadership[^.,;]*',
            r'exec(?:utive)?\s+(?:visibility|comms|thought)[^.,;]*',
            r'ghostwrit[^.,;]*',
            r'linkedin[^.,;]*(?:ghostwrit|thought|post|content)[^.,;]*',
        ]:
            m = re.search(pat, desc, re.IGNORECASE)
            result = m.group(0).strip() if m else ""
            if len(result) > 12:
                return truncate_words(result, 80)
    if framework_id == "3":
        for pat in [r'newsletter[^.,;]*', r'content\s+(?:marketing|creation|development)[^.,;]*']:
            m = re.search(pat, desc, re.IGNORECASE)
            result = m.group(0).strip() if m else ""
            if len(result) > 12:
                return truncate_words(result, 80)
    if framework_id == "5":
        for pat in [r'(?:ai|seo|geo)[^.,;]*(?:citation|metric|analytics|overview)[^.,;]*',
                     r'(?:metric|analytics|reporting)[^.,;]*']:
            m = re.search(pat, desc, re.IGNORECASE)
            result = m.group(0).strip() if m else ""
            if len(result) > 12:
                return truncate_words(result, 80)
    vertical = ""
    for v in ["tech", "B2B", "SaaS", "AI", "fintech", "healthcare", "cyber", "blockchain",
              "Web3", "beauty", "fashion", "lifestyle", "real estate", "finance", "consumer"]:
        if v.lower() in desc.lower():
            vertical = v
            break
    clients = ""
    for pat in [
        r'(?:help(?:ing|s)?|for|cater(?:ing|s)?\s+to)\s+((?:tech\s+)?(?:compan|brand|startup|founder|exec|ceo|business|firm|entrepren)[^.,;]{0,25})',
        r'(?:speciali[sz](?:ing|es)\s+in)\s+([^.,;]{0,35})',
    ]:
        m = re.search(pat, desc, re.IGNORECASE)
        if m:
            clients = truncate_words(m.group(1).strip(), 30)
            break
    if vertical and clients:
        return f"your {vertical} PR work with {clients}"
    elif vertical:
        return f"your {vertical} PR work"
    elif clients:
        return f"your work with {clients}"
    first_sent = desc.split('.')[0].strip()
    return truncate_words(first_sent, 75)


def extract_first_name(email, company_name):
    local = email.split('@')[0].lower()
    if local in NAME_MAP:
        return NAME_MAP[local]
    if '.' in local:
        first = local.split('.')[0]
        if first in NAME_MAP:
            return NAME_MAP[first]
    if '_' in local:
        first = local.split('_')[0]
        if first in NAME_MAP:
            return NAME_MAP[first]
    if local in GENERICS:
        return "there"
    if local.isalpha() and len(local) > 1:
        return local.capitalize()
    return "there"


def count_words(text):
    return len(text.split())


def check_banned(text):
    words = set(text.lower().split())
    return [w for w in words if w in BANNED]


def generate_email(first_name, company_name, description, framework_id):
    fw = FRAMEWORKS[framework_id]
    greeting = random.choice(GREETINGS)
    cta = random.choice(CTAS)
    signal = extract_signal_detail(description, company_name, framework_id)
    body = fw["template"].format(
        greeting=greeting, first_name=first_name,
        signal_detail=signal, cta=cta)
    body = re.sub(r'\.{2,}', '.', body)
    body = re.sub(r'\n{3,}', '\n\n', body).strip()
    return {
        "subject": random.choice(fw["subjects"]), "body": body,
        "framework": framework_id, "framework_name": fw["name"],
        "word_count": count_words(body), "banned": check_banned(body),
        "signal": signal,
    }


def process_batch(input_csv, output_csv, start=0, count=50, framework_stats=None):
    if framework_stats is None:
        framework_stats = {}
    with open(input_csv, 'r') as f:
        all_rows = list(csv.DictReader(f))
    batch = all_rows[start:start + count]
    results = []
    for row in batch:
        email = row.get("email", "").strip()
        company = row.get("Name", "").strip()
        description = row.get("Description", "").strip()
        first_name = extract_first_name(email, company)
        fid = select_framework(description, company)
        gen = generate_email(first_name, company, description, fid)
        framework_stats[fid] = framework_stats.get(fid, 0) + 1
        results.append({
            "first_name": first_name, "last_name": "", "email": email,
            "company_name": company, "domain": row.get("Domain", ""),
            "city": row.get("City", ""), "state": row.get("State", ""),
            "email_subject": gen["subject"], "email_body": gen["body"],
            "framework": gen["framework"], "framework_name": gen["framework_name"],
            "word_count": gen["word_count"], "banned_words": gen["banned"],
            "signal_used": gen["signal"],
        })
    fieldnames = ["first_name", "last_name", "email", "company_name", "domain",
                  "city", "state", "email_subject", "email_body", "framework",
                  "framework_name", "word_count", "banned_words", "signal_used"]
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    return results, framework_stats


if __name__ == "__main__":
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "/opt/data/cache/documents/doc_b75485d0b981_report-3476690ee58fcefbc7ca8410-score-99.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "/tmp/pr_agency_batch.csv"
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    count = int(sys.argv[4]) if len(sys.argv) > 4 else 50
    results, stats = process_batch(input_csv, output_csv, start, count)
    word_counts = [r["word_count"] for r in results]
    banned_counts = sum(1 for r in results if r["banned_words"])
    over_100 = sum(1 for wc in word_counts if wc > 100)
    under_50 = sum(1 for wc in word_counts if wc < 50)
    print(f"Batch: {len(results)} leads")
    print(f"Range: {start}-{start + len(results) - 1}")
    print(f"\nFramework distribution:")
    for fid, cnt in sorted(stats.items(), key=lambda x: -x[1]):
        fw = FRAMEWORKS[fid]
        print(f"  F{fid} ({fw['name'][:50]}...): {cnt}")
    print(f"\nWord count: avg={sum(word_counts)/len(word_counts):.1f}, min={min(word_counts)}, max={max(word_counts)}")
    print(f"Over 100 words: {over_100} ({over_100/len(results)*100:.1f}%)")
    print(f"Under 50 words: {under_50} ({under_50/len(results)*100:.1f}%)")
    print(f"Banned word violations: {banned_counts} ({banned_counts/len(results)*100:.1f}%)")
    print(f"\nOutput: {output_csv}")
    for i, r in enumerate(results[:3]):
        print(f"\n--- Sample {i+1}: {r['first_name']} @ {r['company_name']} (F{r['framework']}) ---")
        print(f"Subject: {r['email_subject']}")
        print(r['email_body'])
        if r["banned_words"]:
            print(f"BANNED: {r['banned_words']}")