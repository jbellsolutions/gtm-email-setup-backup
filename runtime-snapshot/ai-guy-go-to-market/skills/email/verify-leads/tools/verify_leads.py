#!/usr/bin/env python3
"""verify-leads — the cold-email agent's ON-DEMAND client for the self-hosted
Reacher verification gateway.

It reaches Reacher through the sidecar gateway at /verify* using the agent's OWN
revocable consumer key (x-consumer-key), NOT the dashboard's reacher-secret. All
usage shares the SAME hard 10k/24h cap as the dashboard — if the cap is spoken
for, /verify/bulk returns 429 and this tool reports it plainly instead of
sneaking past the budget.

Flow: POST /verify/bulk {emails:[...]} -> job_id ; poll GET /verify/<id> until
done ; return the SENDABLE addresses (deliverable + accept-all/catch-all/role).

Auth resolution (first that exists wins):
  1. env REACHER_CONSUMER_KEY
  2. ~/.hermes/skills/email/verify-leads/config.json  {"consumer_key": "..."}
Endpoint: env REACHER_URL, else https://verify.usingaitoscale.com

Stdlib only — no install. Usage:
  verify_leads.py a@x.com b@y.com                 # emails as args
  verify_leads.py leads.csv                        # a CSV/TXT file (auto-detect email column)
  cat leads.txt | verify_leads.py -                # stdin
  verify_leads.py leads.csv --json                 # machine-readable (for the agent)
  verify_leads.py leads.csv -o out/sendable.csv    # also write the sendable list to a file
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "https://verify.usingaitoscale.com"
CONFIG = os.path.expanduser("~/.hermes/skills/email/verify-leads/config.json")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def _die(msg, code=2, **extra):
    if "--json" in sys.argv:
        print(json.dumps({"ok": False, "error": msg, **extra}))
    else:
        print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def _key():
    k = os.environ.get("REACHER_CONSUMER_KEY", "").strip()
    if k:
        return k
    try:
        with open(CONFIG) as f:
            k = (json.load(f).get("consumer_key") or "").strip()
            if k:
                return k
    except (OSError, ValueError):
        pass
    _die("no consumer key — set REACHER_CONSUMER_KEY or write "
         f"{CONFIG} with {{\"consumer_key\": \"...\"}}")


def _base():
    return os.environ.get("REACHER_URL", DEFAULT_URL).rstrip("/")


def _req(method, path, key, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"x-consumer-key": key}
    if data:
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(_base() + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except ValueError:
            return e.code, {}
    except urllib.error.URLError as e:
        _die(f"cannot reach {_base()} ({e.reason}) — check REACHER_URL / DNS / network", 3)


def _collect_emails(args):
    """args = the positional inputs (emails, file paths, or '-' for stdin)."""
    raw = []
    for a in args:
        if a == "-":
            raw.append(sys.stdin.read())
        elif os.path.isfile(a):
            with open(a, encoding="utf-8", errors="ignore") as f:
                raw.append(f.read())
        else:
            raw.append(a)
    found, seen = [], set()
    for chunk in raw:
        for m in EMAIL_RE.findall(chunk):
            e = m.strip().lower()
            if e not in seen:
                seen.add(e)
                found.append(e)
    return found


def main():
    argv = [a for a in sys.argv[1:]]
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    out_path = None
    if "-o" in argv:
        i = argv.index("-o")
        out_path = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    poll_timeout = 900  # 15 min ceiling
    if "--timeout" in argv:
        i = argv.index("--timeout")
        poll_timeout = int(argv[i + 1]); del argv[i:i + 2]

    # re-poll an existing job (e.g. after a timeout): verify_leads.py --status 123
    if "--status" in argv:
        i = argv.index("--status")
        job_id = int(argv[i + 1])
        key = _key()
        st, body = _req("GET", f"/verify/{job_id}", key)
        if st != 200:
            _die(f"status check failed (HTTP {st}): {body.get('error','unknown')}", 6, http=st, job_id=job_id)
        sendable = body.get("sendable") or []
        if as_json:
            print(json.dumps({"ok": True, **body}))
        else:
            print(f"job {job_id}: {body.get('status')} — {body.get('processed',0)}/{body.get('total',0)} "
                  f"checked · SENDABLE {len(sendable)}")
        return

    if not argv:
        _die("no input — pass emails, a CSV/TXT file, or '-' for stdin")
    emails = _collect_emails(argv)
    if not emails:
        _die("no email addresses found in the input")

    key = _key()

    # 1. submit
    st, body = _req("POST", "/verify/bulk", key, {"emails": emails})
    if st == 401:
        _die("consumer key rejected (invalid or revoked) — this key may have been "
             "turned off in api_consumers", 4, http=401)
    if st == 429:
        _die(f"shared daily cap reached ({body.get('used','?')}/{body.get('cap','?')} "
             f"used, {body.get('remaining',0)} left) — the dashboard and agent share ONE "
             "10k/24h budget; try again later", 5, http=429, **{k: body.get(k) for k in ('used', 'cap', 'remaining')})
    if st != 200 or not body.get("job_id"):
        _die(f"submit failed (HTTP {st}): {body.get('error','unknown')}", 6, http=st)
    job_id = body["job_id"]
    if not as_json:
        print(f"submitted {len(emails)} emails → job {job_id} (consumer={body.get('consumer')}). polling…",
              file=sys.stderr)

    # 2. poll
    start = time.monotonic()
    last = {}
    while True:
        st, body = _req("GET", f"/verify/{job_id}", key)
        if st != 200:
            _die(f"status check failed (HTTP {st}): {body.get('error','unknown')}", 6, http=st, job_id=job_id)
        last = body
        if body.get("status") == "completed":
            break
        if time.monotonic() - start > poll_timeout:
            # not an error — return partial; the job keeps running server-side
            if not as_json:
                print(f"timed out after {poll_timeout}s; job {job_id} still running server-side "
                      f"({body.get('processed',0)}/{body.get('total',0)}). Re-poll later:",
                      file=sys.stderr)
                print(f"  verify_leads.py --status {job_id}", file=sys.stderr)
            break
        if not as_json:
            print(f"  … {body.get('processed',0)}/{body.get('total',0)}", file=sys.stderr)
        time.sleep(6)

    sendable = last.get("sendable") or []
    result = {
        "ok": True,
        "job_id": job_id,
        "status": last.get("status"),
        "total": last.get("total"),
        "processed": last.get("processed"),
        "summary": last.get("summary", {}),
        "sendable_count": len(sendable),
        "sendable": sendable,
    }

    if out_path and sendable:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("email\n")
            f.writelines(e + "\n" for e in sendable)
        result["written"] = out_path

    if as_json:
        print(json.dumps(result))
    else:
        s = last.get("summary", {})
        print(f"\njob {job_id}: {last.get('status')} — {last.get('processed',0)}/{last.get('total',0)} checked")
        if s:
            print("  buckets: " + " · ".join(f"{k}={v}" for k, v in sorted(s.items())))
        print(f"  SENDABLE (deliverable + accept-all): {len(sendable)}")
        if out_path and sendable:
            print(f"  written → {out_path}")
        elif sendable:
            for e in sendable:
                print("    " + e)


if __name__ == "__main__":
    main()
