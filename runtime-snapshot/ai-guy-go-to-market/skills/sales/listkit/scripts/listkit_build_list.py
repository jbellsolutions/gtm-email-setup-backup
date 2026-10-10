#!/usr/bin/env python3
"""Build and scrape a list on the authenticated ListKit session.

REQUIRES: BROWSER_USE_API_KEY env var, and a SESSION_ID from listkit_login.py.
USAGE: python3 listkit_build_list.py <SESSION_ID> "<ai prompt>"

Example:
    python3 listkit_build_list.py e0bab6f5-0eb7-419b-84c3-cedd1a1206ce \\
        "manufacturing software vendors helping automotive suppliers"
"""
import sys
from browser_use_sdk.v3 import BrowserUse, BuModel

if len(sys.argv) < 3:
    print("Usage: python3 listkit_build_list.py <SESSION_ID> \"<ai prompt>\"")
    sys.exit(1)

session_id = sys.argv[1]
prompt = sys.argv[2]

client = BrowserUse()

result = client.run(
    session_id=session_id,
    task=f"""Go to https://app.listkit.io
Use the AI Company Search to find: {prompt}
Wait for results to load.
Click on the "People" view to see individual contacts.
Extract all visible contacts: name, title, company, email if visible.
Return the results as a JSON array.
If asked to export/checkout, STOP and report what you see — don't consume credits.""",
    max_steps=20,
)
print(f'STATUS: {result.status}')
print(f'OUTPUT: {result.output}')
