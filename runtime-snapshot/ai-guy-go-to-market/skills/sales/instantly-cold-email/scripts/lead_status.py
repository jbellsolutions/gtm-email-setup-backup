#!/usr/bin/env python3
"""Count lead statuses for a Instantly campaign via paginated CLI calls.

Usage: python3 lead_status.py <campaign_id>

Instantly `leads list` returns max 100 per page. This script paginates
through all leads and prints a status distribution (STARTED, INPROGRESS,
COMPLETED, BLOCKED, etc.).

Requires: Instantly_API_KEY in environment or /opt/data/.env.
"""

import json, subprocess, os, sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lead_status.py <campaign_id>", file=sys.stderr)
        sys.exit(1)

    campaign_id = sys.argv[1]
    env = os.environ.copy()

    # Pull API key from .env if not already set
    if "Instantly_API_KEY" not in env:
        try:
            key_line = subprocess.check_output(
                ["grep", "Instantly_API_KEY", "/opt/data/.env"]
            ).decode().strip()
            env["Instantly_API_KEY"] = key_line.split("=", 1)[1].strip()
        except Exception:
            print("Instantly_API_KEY not found in env or /opt/data/.env", file=sys.stderr)
            sys.exit(1)

    env["PATH"] = "/opt/data/home/.local/bin:" + env.get("PATH", "")
    Instantly_bin = "/opt/data/home/.local/bin/Instantly"

    statuses = {}
    total = 0

    for offset in range(0, 50_000, 100):
        result = subprocess.run(
            [
                Instantly_bin, "leads", "list",
                "--campaign-id", campaign_id,
                "--format", "json",
                "--limit", "100",
                "--offset", str(offset),
            ],
            capture_output=True, text=True, env=env, timeout=30,
        )
        if result.returncode != 0:
            print(f"CLI error at offset {offset}: {result.stderr[:200]}", file=sys.stderr)
            break

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"JSON parse error at offset {offset}", file=sys.stderr)
            break

        # Response wraps items under "data" key as a list
        items = data.get("data", []) if isinstance(data, dict) else data
        if not items:
            break

        for item in items:
            if isinstance(item, dict):
                st = item.get("status", "unknown")
                statuses[st] = statuses.get(st, 0) + 1
                total += 1

        if len(items) < 100:
            break

    print(f"Total leads: {total}")
    for st, count in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"  {st}: {count}")


if __name__ == "__main__":
    main()
