# Composio API Endpoint Discovery (July 20, 2026)

## Current Production Endpoints

**Base URL:** `https://backend.composio.dev`

### Version Matrix

| Version | Status | Example Path | Notes |
|---|---|---|---|
| v2 | Deprecated | `/api/v2/apps` | Returns "Please upgrade to v3 APIs" — still works for some endpoints |
| v3 | 404 | `/api/v3/apps` | Returns Next.js 404 page for most paths |
| v3.1 | Production ✅ | `/api/v3.1/connected_accounts` | Current version. Use this. |

### Key v3.1 Endpoints

```bash
# List connected accounts
GET /api/v3.1/connected_accounts

# Get single account
GET /api/v3.1/connected_accounts/{nanoid}

# Refresh account token
POST /api/v3.1/connected_accounts/{nanoid}/refresh

# Get account status
GET /api/v3.1/connected_accounts/{nano_id}/status
```

## Auth

- **Header:** `x-api-key: <your_api_key>`
- **Not:** `Authorization: Bearer <key>` (the old v2 format; works on some endpoints but x-api-key is correct for v3.1)
- **Key format:** The API key from Settings → API Keys. Keys starting with `ck_` or `ak_` return `APIKey_InvalidAPIKey` (code 801).

## Python SDK Version

- **`composio_core` 0.7.21** — Deprecated. Do not use.
- **`composio` 0.18.0** — Current. `from composio import Composio`
- **`composio_client` 1.42.0** — Auto-installed dependency, contains the REST client used internally.

## Discovery Process

1. Tried `backend.composio.io` — doesn't resolve (NXDOMAIN)
2. Tried `api.composio.dev` — doesn't resolve (NXDOMAIN)
3. Found `backend.composio.dev` in composio_client source: `_client.py:78: "production": "https://backend.composio.dev"`
4. v2 apps endpoint works but returns deprecation notice
5. v3 paths 404 until trying `/api/v3.1/` which the Python package uses internally
6. Found v3.1 path templates in `composio_client/resources/connected_accounts.py` using `path_template("/api/v3.1/connected_accounts/{nanoid}", ...)`
