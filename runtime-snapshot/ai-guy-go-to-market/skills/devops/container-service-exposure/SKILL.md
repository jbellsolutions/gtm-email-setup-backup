---
name: container-service-exposure
description: "Expose locally-running services (web terminals, APIs, UIs) from restricted containerized environments where you lack root access, sudo, or direct port forwarding. Covers gotty, SSH reverse tunnels, bore, binary downloads without curl, and /proc/net diagnostics."
version: 1.0.0
---

# Exposing Services from Restricted Containers

When you need to make a locally-running service (web terminal, API, dashboard) reachable from outside, but you're in a Docker container behind NAT with no root, no sudo, no curl, and only a single exposed port.

## When to Use

- User wants to access a TUI, web terminal, or local HTTP service from their browser
- You're in a Docker container; the only exposed port is the Hermes gateway (9119)
- `apt-get install` fails (no root), binaries need to be downloaded manually
- Public IP is unreachable (NAT/firewall between container and internet)
- Need to quickly serve a terminal session over HTTP

## Quick Diagnostic: What's Actually Happening

```bash
# Check listening ports (no netstat needed)
cat /proc/net/tcp    # IPv4
cat /proc/net/tcp6   # IPv6 — gotty often binds here only

# Ports are in hex — port 8765 = 0x223D, port 9119 = 0x239F
# Status 0A = LISTEN
```

If your service shows in `/proc/net/tcp6` but not `/proc/net/tcp`, it's IPv6-only. The `-a 0.0.0.0` flag on gotty may not help — the container's IPv4 is Docker bridge (172.x.x.x), and the public IP won't forward to it.

## Serving a Terminal Over HTTP: gotty

gotty is a single binary (~13MB) that wraps any command in a web terminal. No dependencies.

### Install (no curl)

```python
import urllib.request, tarfile, os, stat

# Download from GitHub releases
url = "https://github.com/sorenisanerd/gotty/releases/download/v1.5.0/gotty_v1.5.0_linux_amd64.tar.gz"
urllib.request.urlretrieve(url, "/tmp/gotty.tar.gz")

with tarfile.open("/tmp/gotty.tar.gz", "r:gz") as tar:
    tar.extractall("/tmp")
os.chmod("/tmp/gotty", stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
```

### Run

```bash
# Start hermes TUI as a web terminal
/tmp/gotty -w -p 8765 --title-format "Hermes TUI" /opt/hermes/.venv/bin/hermes

# Bind to all interfaces (may not help in containers)
/tmp/gotty -w -a 0.0.0.0 -p 8765 /opt/hermes/.venv/bin/hermes
```

### Verify

```bash
cat /proc/net/tcp6 | grep 223D   # port 8765 in hex
```

## Tunneling Out

When the container has outbound SSH but the port isn't publicly exposed, tunnel through a free service.

### Approach 1: bore (Rust binary, no auth needed)

```python
# Download bore
url = "https://github.com/ekzhang/bore/releases/download/v0.5.2/bore-v0.5.2-x86_64-unknown-linux-musl.tar.gz"
urllib.request.urlretrieve(url, "/tmp/bore.tar.gz")
# Extract and chmod as above
```

```bash
/tmp/bore local 8765 --to bore.pub
# If it works, prints a bore.pub URL. If silent, bore.pub may be down.
```

### Approach 2: SSH reverse tunnels (localhost.run / serveo.net)

```bash
# localhost.run — exposes port as a random subdomain
ssh -o StrictHostKeyChecking=no -R 80:localhost:8765 nokey@localhost.run

# serveo.net — often more reliable but slower
ssh -o StrictHostKeyChecking=no -R 80:localhost:8765 serveo.net
```

Both are free, no account needed. The URL appears in stdout after connection. **Reliability is spotty** — if you get no output after 15s, the service is likely down.

### Approach 3: cloudflared (requires token)

If a Cloudflare tunnel token is available, cloudflared is the most reliable option. Download the binary (same pattern as gotty/bore) and run:

```bash
cloudflared tunnel --url http://localhost:8765
```

## Fallback: PTY Relay Through Hermes Tools

When ALL tunneling fails, use the process tool's PTY mode as a relay:

```bash
# Start hermes in background PTY
hermes &
# Then relay I/O through process tool (write/submit to send commands, poll/wait for output)
```

This gives the user a relayed TUI through whatever messaging platform they're already on (Telegram, Slack, etc.). Slower than a direct terminal but works reliably without any external dependencies.

## General Patterns for Restricted Containers

| Problem | Solution |
|---------|----------|
| No `curl` | Python `urllib.request.urlretrieve()` |
| No `wget` | Same as above |
| No root / sudo | Download static binaries, chmod +x |
| No `apt-get` | Download `.tar.gz` releases from GitHub |
| Can't install npm packages globally | Use `npx -y` (already works) |
| Port not in `/proc/net/tcp` | Check `/proc/net/tcp6` — likely IPv6-only |
| Public IP unreachable | Use SSH tunnel or bore to punch out |
| `ss` / `netstat` missing | Read `/proc/net/tcp` and `/proc/net/tcp6` directly |

## Static Content Publishing (When All Tunnels Fail)

When you just need to share static HTML/text content (not a running service), skip the tunnels entirely and use a pastebin:

### dpaste.com (reliable, no auth needed)

```python
import urllib.request
data = open('/path/to/file.html', 'rb').read()
req = urllib.request.Request('https://dpaste.com/api/v2/',
    data=urllib.parse.urlencode({'content': data.decode(), 'expiry_days': '7', 'format': 'url'}).encode(),
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
resp = urllib.request.urlopen(req, timeout=10)
print(resp.read().decode())  # https://dpaste.com/XXXXXXXXX
```

Append `.txt` for raw access: `https://dpaste.com/XXXXXXXXX.txt`. Works for any text content (HTML, JSON, code). No rendering — it's a pastebin, not a hosting service. For agent-consumable content, send the raw `.txt` URL.

### Other Options (YMMV)

- **transfer.sh**: `curl --upload-file file.html https://transfer.sh/file.html` — often down
- **ix.io**: `cat file | curl -F 'f:1=<-' ix.io` — down as of July 2026
- **GitHub Gist**: requires auth, but persistent

## Pitfalls

- **gotty binds IPv6 by default** — even with `-a 0.0.0.0`, it still shows only `[::]:8765` and internal IPs. The container's Docker bridge IP (172.x.x.x) is NOT routable from the internet.
- **Free SSH tunnel services are unreliable** — localhost.run and serveo.net go down frequently. Don't spend more than 2 attempts on them.
- **bore.pub may be silent** — if the binary runs but produces no output, the relay server is unreachable. Kill it and move on.
- **Python urllib from sandbox vs terminal** — the execute_code sandbox may have different network access than the terminal tool. When downloading binaries, use the terminal tool with Python's urllib directly, not the execute_code sandbox.
- **Don't tunnel for tunnel's sake** — if the user is already on Telegram/Discord/Slack, the PTY relay approach gives them a working TUI without any networking work.
