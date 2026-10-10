# Resumable research crawler — debugging narrative and validated pattern

Session context (2026-09-03): refreshing per-lead website research for ~24,100 domains (fitness/wellness lead list) ahead of a 22-touch per-lead cold-email build. The working pattern below was validated live at scale; the regex failure is the durable lesson.

## Symptoms (do not misdiagnose)

- A threaded crawler (ThreadPoolExecutor, 24-48 workers) writing to an append-only JSONL produced **zero output for 9+ minutes** while `ps` showed 49 threads alive, ~83% of a single core, and open sockets.
- A **small** batch of the identical code (40 domains, foreground) finished in 3.8s. 400 domains in 14.9s.
- DNS resolution and TCP connect probes were fast (0.02-0.13s). Not a network, DNS, or credential problem.
- The stall reproduced in both background and foreground once the batch was large enough to include a pathological page.

## Root cause

A single unbounded regex in the HTML `extract()` function:

```python
re.search(r'<meta[^>]+name="description"[^>]+content=["\'](.*?)["\']', html, re.I | re.S)
```

On multi-megabyte, tag-sparse pages this goes quadratic, and because Python regexes hold the GIL, **one pathological page freezes the entire thread pool**. Small test batches pass because they happen not to include a huge page. Background-vs-foreground was a red herring; the real variable was batch size (probability of including a pathological page).

## Diagnosis method that worked

1. Confirm the process is alive and working (`ps`, `/proc/<pid>/status` thread count, open socket count).
2. Time DNS, then TCP connect, then a full fetch on sample domains — isolate the layer.
3. Run fetch-only over a few hundred pending domains (no extract). If that flies, the stall is in post-processing.
4. Extract alone on the **largest real captured pages** (1MB+ HTML). Time it. The hang reproduces instantly.

## Fix: bounded inputs and linear patterns

```python
def extract(html):
    head = html[:60000]          # title/meta/description live in the document head
    work = html[:400000]         # cap body processing
    title = m.group(1) if (m := re.search(r'<title[^>]*>(.*?)</title>', head, re.I | re.S)) else ''
    title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', title)).strip()[:200]
    # meta description: string find, not a giant regex
    i = head.lower().find('name="description"')
    desc = ''
    if i != -1:
        seg = head[i:i+600]
        j = seg.find('content="')
        if j != -1:
            seg2 = seg[j+9:]
            k = seg2.find('"')
            if k != -1: desc = seg2[:k].strip()[:300]
    h1 = ''
    m3 = re.search(r'<h1[^>]*>(.*?)</h1>', work, re.I | re.S)
    if m3: h1 = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m3.group(1))).strip()[:200]
    body = re.sub(r'<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>|<noscript\b[^>]*>.*?</noscript\s*>', ' ', work, flags=re.I | re.S)
    text = re.sub(r'<[^<>]{0,200}>', ' ', body)          # bounded tag match, not <[^>]+>
    text = re.sub(r'\s{2,}', ' ', text).strip()[:4000]
    return title, desc, h1, text
```

Validate before relaunch: extract must stay in the low milliseconds even on the biggest captured pages (observed 0.006-0.032s on 67KB-1.2MB pages).

## Validated resumable crawl pattern

- **Checkpoint file:** append-only JSONL, one record per `domain_key` (`{'domain_key', 'emails': [...], 'research': {...}}`), written with `buffering=1` + flush per record under a lock. Dedupe multiple emails sharing one domain — one fetch serves many leads.
- **Skip-done on startup:** load existing keys from the checkpoint; also skip leads whose research is already good in an older corpus.
- **Time budget:** `FETCH_BUDGET` env var; the loop checks elapsed time every record, breaks cleanly, cancels pending futures, and exits so the next call resumes from the checkpoint. This makes long crawls safe to run as repeated budgeted foreground calls instead of an unattended background process.
- **Workers:** 32 was sufficient once extract was fixed; higher counts did not help because dead domains exit fast and live pages are milliseconds.

Verified run: 23,707 domains in 8.8 minutes, 18,165 ok (76.6%); a second pass closed 388 stragglers (327 more ok) in 1.1 minutes.

## Do not encode as a rule

- "Background terminals stall" is NOT the lesson — the regex was the root cause in both modes. Budgeted foreground chunks were chosen operationally because they resume cleanly, not because background is broken.
