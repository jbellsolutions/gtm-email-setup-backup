#!/usr/bin/env python3
"""Login to ListKit via Google OAuth using Browser Use Cloud persistent profile.

REQUIRES: BROWSER_USE_API_KEY environment variable set.
USAGE: python3 listkit_login.py

This creates a session and runs the login task. Google will trigger 2FA —
the user must approve on their iPhone (YouTube app). Once approved, the
session stays alive with keep_alive=True and the profile persists cookies.

After login, note the SESSION_ID printed — use it in listkit_build_list.py
to build and scrape lists without re-authenticating.
"""
from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode

client = BrowserUse()

# Create persistent profile (reuse across sessions)
try:
    profiles = client.profiles.list()
    profile = next((p for p in profiles if p.name == 'listkit'), None)
    if not profile:
        profile = client.profiles.create(
            name='listkit',
            description='ListKit Google OAuth login profile'
        )
        print(f'Created new profile: {profile.id}')
    else:
        print(f'Using existing profile: {profile.id}')
except Exception:
    profile = client.profiles.create(
        name='listkit',
        description='ListKit Google OAuth login profile'
    )
    print(f'Created new profile: {profile.id}')

# Create session with anti-detection + US proxy
session = client.sessions.create(
    model=BuModel.claude_sonnet_4_6,
    proxy_country_code=ProxyCountryCode.us,
    keep_alive=True,
    profile_id=str(profile.id),
)
print(f'SESSION_ID: {session.id}')
print(f'LIVE_URL: {session.live_url}')

# Run login task
result = client.run(
    session_id=str(session.id),
    task="""Go to https://next.listkit.io/login
Click the "Log In with Google" button.
On the Google sign-in page, enter email: justin@usingaitoscale.com
Click Next.
Enter password: UsingAITOScale2o24$
Click Next.
If Google asks for 2FA verification ("Verify it's you"), STOP and report the number.
The user will approve on their iPhone.
If login succeeds, navigate to https://app.listkit.io and describe the dashboard.""",
    max_steps=15,
)
print(f'STATUS: {result.status}')
print(f'OUTPUT: {result.output}')
print(f'\nSAVE THIS SESSION_ID: {session.id}')
