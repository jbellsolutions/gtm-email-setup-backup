#!/usr/bin/env python3
"""Composio client wrapper — handles venv sys.path and returns a configured client.

Usage:
    python3 /opt/data/skills/productivity/composio/scripts/run_composio.py [--check]
    
    --check: verify API key works, print connected accounts, exit 0/1
    (no args): returns a JSON summary of connected accounts
"""

import sys
import os
import json

# Ensure the system site-packages is in the path (Composio installed here)
SITE_PACKAGES = '/opt/data/home/.local/lib/python3.13/site-packages'
if SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

def get_client():
    api_key = os.environ.get("COMPOSIO_API_KEY") or os.popen(
        "grep COMPOSIO_API_KEY /opt/data/.env | cut -d= -f2"
    ).read().strip()
    
    if not api_key:
        print(json.dumps({"error": "COMPOSIO_API_KEY not set"}))
        sys.exit(1)
    
    from composio import Composio
    return Composio(api_key=api_key)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    
    try:
        client = get_client()
        accounts = client.connected_accounts.list()
        
        result = {
            "status": "ok",
            "connected_accounts": len(accounts),
            "accounts": [
                {"id": getattr(a, "id", "?"), "app": getattr(a, "app_name", "?")}
                for a in accounts
            ]
        }
        print(json.dumps(result, indent=2))
        
        if args.check:
            sys.exit(0 if len(accounts) > 0 else 1)
            
    except Exception as e:
        msg = str(e)
        is_auth_error = "401" in msg or "Invalid API key" in msg
        print(json.dumps({
            "status": "error",
            "error": msg[:300],
            "auth_error": is_auth_error,
            "suggested_fix": "Get a valid API key from https://app.composio.dev → Settings → API Keys" if is_auth_error else None
        }, indent=2))
        sys.exit(1 if is_auth_error else 2)

if __name__ == "__main__":
    main()
