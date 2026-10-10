#!/usr/bin/env python3
"""
Apple Podcasts Search API — free, unauthenticated, no rate limits.
Ideal for researching podcast host leads (SpeakerAgent Beta bookings).

Usage:
    python3 apple_podcasts_search.py <search_term> [--fetch-rss] [--limit N]

Examples:
    python3 apple_podcasts_search.py "house of impact"
    python3 apple_podcasts_search.py "geni cor" --fetch-rss
    python3 apple_podcasts_search.py "business growth talks" --limit 3 --fetch-rss

Output:
    Podcast name, host name, RSS feed URL, Apple Podcasts URL, episode count.
    With --fetch-rss: also fetches and parses the RSS feed for episode titles,
    channel description (host bio), and recent episode descriptions.

Exit codes:
    0 = at least one podcast found
    1 = no results
    2 = network/curl error
    3 = JSON parse error
"""

import subprocess
import json
import re
import html as _html
import sys
import argparse


def search_apple_podcasts(term, limit=5):
    """Search Apple Podcasts by name/host. Returns list of result dicts."""
    # URL-encode the search term
    encoded = term.replace(" ", "+")
    url = f"https://itunes.apple.com/search?term={encoded}&media=podcast&limit={limit}"

    r = subprocess.run(
        ["curl", "-s", url,
         "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
         "--max-time", "10"],
        capture_output=True, text=True
    )

    if r.returncode != 0:
        print(f"ERROR: curl failed (exit {r.returncode})", file=sys.stderr)
        sys.exit(2)

    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: JSON parse failed. Raw: {r.stdout[:200]}", file=sys.stderr)
        sys.exit(3)

    return data.get("results", [])


def fetch_rss_feed(feed_url, max_episodes=10):
    """Fetch and parse an RSS feed for episode-level detail."""
    r = subprocess.run(
        ["curl", "-s", "-L", feed_url,
         "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
         "--max-time", "15"],
        capture_output=True, text=True
    )

    rss = r.stdout

    # Channel description
    chan_desc = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", rss, re.DOTALL)
    desc = ""
    if chan_desc:
        desc = chan_desc.group(1).strip()
        desc = re.sub(r"<[^>]+>", "", desc)
        desc = _html.unescape(desc).strip()

    # Episode titles
    ep_blocks = re.findall(r"<item>(.*?)</item>", rss, re.DOTALL)
    episodes = []
    for block in ep_blocks[:max_episodes]:
        title_m = re.search(r"<title>(.*?)</title>", block, re.DOTALL)
        desc_m = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", block, re.DOTALL)
        title = ""
        if title_m:
            title = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", title_m.group(1)).strip()
        ep_desc = ""
        if desc_m:
            ep_desc = desc_m.group(1).strip()
            ep_desc = re.sub(r"<[^>]+>", "", ep_desc)
            ep_desc = _html.unescape(ep_desc).strip()

        episodes.append({"title": title, "description": ep_desc[:300]})

    total_episodes = len(re.findall(r"<item>", rss))

    return {
        "channel_description": desc[:500],
        "total_episodes": total_episodes,
        "recent_episodes": episodes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Search Apple Podcasts for podcast host research"
    )
    parser.add_argument("search_term", help="Podcast name or host name to search for")
    parser.add_argument("--fetch-rss", action="store_true",
                        help="Also fetch and parse the RSS feed for episode detail")
    parser.add_argument("--limit", type=int, default=5,
                        help="Max number of results (default: 5)")
    args = parser.parse_args()

    results = search_apple_podcasts(args.search_term, args.limit)

    if not results:
        print("No podcasts found.")
        sys.exit(1)

    print(f"Found {len(results)} podcast(s):\n")

    for i, res in enumerate(results):
        name = res.get("collectionName", "?")
        host = res.get("artistName", "?")
        feed_url = res.get("feedUrl", "")
        apple_url = res.get("trackViewUrl", "")
        track_count = res.get("trackCount", "?")

        print(f"  [{i+1}] {name}")
        print(f"      Host: {host}")
        print(f"      Episodes: {track_count}")
        print(f"      RSS: {feed_url}")
        print(f"      Apple: {apple_url}")

        if args.fetch_rss and feed_url:
            print(f"      Fetching RSS feed...")
            rss_data = fetch_rss_feed(feed_url)
            if rss_data["channel_description"]:
                print(f"      Channel description: {rss_data['channel_description'][:300]}")
            print(f"      Total episodes in feed: {rss_data['total_episodes']}")
            if rss_data["recent_episodes"]:
                print(f"      Recent episodes:")
                for ep in rss_data["recent_episodes"][:5]:
                    print(f"        - {ep['title'][:100]}")
                    if ep["description"]:
                        print(f"          {ep['description'][:200]}")

        print()

    sys.exit(0)


if __name__ == "__main__":
    main()
