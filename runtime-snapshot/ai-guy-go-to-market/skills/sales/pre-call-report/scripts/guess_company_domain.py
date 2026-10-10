#!/usr/bin/env python3
"""
Guess a lead's company domain from their email handle.

Used as a last-ditch research fallback when ALL search engines (DDG HTML, Google,
Bing, Yandex) are blocked/rate-limited from the VPS. Takes a Gmail/personal address
like `genicormedia@gmail.com` and tries DNS resolution for common TLD variants of
the email handle. If any resolve, prints the working domain(s) — then the agent
can fetch that website via curl for pre-call report Section 3 research.

Usage:
    python3 scripts/guess_company_domain.py genicormedia@gmail.com
    python3 scripts/guess_company_domain.py genicormedia@gmail.com --fetch
        # --fetch also curls the first resolving domain and prints first 1500 chars

Exit codes:
    0 = at least one domain resolved
    1 = no domains resolved (lead has no discoverable business website — report is "thin")
    2 = bad input (no @ in email)
"""

import socket
import sys
import subprocess
import re


# TLDs to try, in priority order (most common for solo creators / media brands first)
TLDS = [
    "com", "co", "media", "io", "ai", "net", "org", "me", "tv",
    "agency", "studio", "podcast", "show",
]

# Hyphenation variants to try for multi-word handles
# e.g. `genicormedia` -> try `geni-cormedia.com`, `genicor-media.com`
def handle_variants(handle):
    variants = [handle]
    # Try common two-word splits if handle looks like Word1Word2
    # Heuristic: split at lowercase-uppercase boundary OR at common word boundaries
    # Keep it simple — just try hyphenating at the midpoint and a few common splits
    if len(handle) > 8:
        mid = len(handle) // 2
        variants.append(handle[:mid] + "-" + handle[mid:])
    # Try splitting at "media", "cor", "agency", "studio" if present
    for sep_word in ["media", "cor", "agency", "studio", "podcast", "show"]:
        if handle.lower().endswith(sep_word) and len(handle) > len(sep_word) + 2:
            prefix = handle[: -len(sep_word)]
            variants.append(prefix + "-" + sep_word)
            variants.append(prefix + sep_word)  # already in list but idempotent
    # Dedupe preserving order
    seen = set()
    out = []
    for v in variants:
        if v not in seen and v:
            seen.add(v)
            out.append(v)
    return out


def resolve_domain(domain):
    """Return True if domain resolves to an A record."""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False
    except socket.herror:
        return False


def main():
    if len(sys.argv) < 2 or "@" not in sys.argv[1]:
        print("Usage: guess_company_domain.py <email> [--fetch]", file=sys.stderr)
        sys.exit(2)

    email = sys.argv[1].strip().lower()
    handle = email.split("@")[0]
    do_fetch = "--fetch" in sys.argv

    # Strip common numeric suffixes from handles like "john.smith123"
    handle = re.sub(r"\d+$", "", handle)

    candidates = []
    for variant in handle_variants(handle):
        for tld in TLDS:
            candidates.append(f"{variant}.{tld}")

    # Also try the full handle as a subdomain of common platforms
    for platform in ["substack.com", "medium.com", "linkedin.com/in", "youtube.com/c"]:
        candidates.append(f"{handle}.{platform}")

    resolved = []
    for domain in candidates:
        if resolve_domain(domain):
            resolved.append(domain)
            print(f"RESOLVED: {domain}")

    if not resolved:
        print(f"\nNo domains resolved for handle '{handle}'.", file=sys.stderr)
        print("Lead has no discoverable business website — report is 'thin'.", file=sys.stderr)
        print("Flag all Section 2-5 unknowns in Open Items per the hard rule.", file=sys.stderr)
        sys.exit(1)

    print(f"\n{len(resolved)} domain(s) resolved for handle '{handle}'.")

    if do_fetch:
        # Curl the first resolved domain and print first 1500 chars of text
        target = f"https://{resolved[0]}"
        print(f"\n--- Fetching {target} ---")
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "10", target],
                capture_output=True, text=True, timeout=15,
            )
            html = result.stdout
            # Strip tags/scripts/styles for readability
            html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()
            print(text[:1500] if text else "(no readable text)")
        except subprocess.TimeoutExpired:
            print("(curl timed out)")
        except Exception as e:
            print(f"(curl failed: {e})")

    sys.exit(0)


if __name__ == "__main__":
    main()
