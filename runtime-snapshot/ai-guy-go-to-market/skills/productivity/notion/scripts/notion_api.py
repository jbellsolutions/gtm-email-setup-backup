#!/usr/bin/env python3
"""
Notion API helper for Hermes Agent.
Usage: python3 notion_api.py <method> <endpoint> [json_body]

Examples:
  python3 notion_api.py POST /v1/search '{"query": "Clients"}'
  python3 notion_api.py GET /v1/databases/abc123
  python3 notion_api.py POST /v1/pages '{"parent":{"database_id":"xxx"},"properties":{...}}'
  python3 notion_api.py PATCH /v1/pages/abc123 '{"properties":{"Status":{"select":{"name":"Done"}}}}'
  python3 notion_api.py PATCH /v1/blocks/abc123/children '{"children":[...]}'
  python3 notion_api.py POST /v1/data_sources/abc123/query '{"filter":{...}}'
"""
import urllib.request, urllib.error, json, sys, os

API_KEY = os.environ.get("NOTION_API_KEY", "")
BASE = "https://api.notion.com"
VERSION = "2025-09-03"

def call(method, endpoint, body=None):
    url = f"{BASE}{endpoint}" if endpoint.startswith("/") else f"{BASE}/{endpoint}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    })
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read()) if e.fp else {"status": e.code, "message": str(e)}
        print(json.dumps(err, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    method = sys.argv[1].upper()
    endpoint = sys.argv[2]
    body = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    result = call(method, endpoint, body)
    print(json.dumps(result, indent=2))
