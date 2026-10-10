---
name: hermes-config-operations
description: "Use when changing Hermes settings — MoA references/aggregator, providers, models, toolsets, or any config.yaml key — especially when direct writes are blocked by Hermes config protection."
version: 1.0.0
author: Adapted from vivid-plover-t4hv.here.now
license: MIT
metadata:
  hermes:
    tags: [hermes, configuration, moa, providers, mcp]
    related_skills: [hermes-agent]
---

# Hermes Config Operations

## Overview

Safely edit `~/.hermes/config.yaml` when direct writes are blocked by Hermes config protection. Use supported edit pathways, make the smallest possible change, back up first, and verify through Hermes' domain-specific commands rather than trusting a raw YAML read.

## When to Use

- Changing Hermes providers, models, toolsets, MoA references or aggregators, MCP server settings, or other config keys.
- Direct `patch` or `write_file` operations against `~/.hermes/config.yaml` are refused.
- An MCP OAuth login times out or discovery fails after authentication.

## Golden Rules

1. **Back up first.**
   ```bash
   cp -p ~/.hermes/config.yaml ~/.hermes/config.yaml.bak.$(date +%Y%m%d%H%M%S)
   ```
2. **Prefer domain subcommands over raw YAML.** Commands such as `hermes moa`, `hermes model`, and `hermes fallback` know the supported schema. Check `hermes <cmd> --help`.
3. **Verify with the authority command, not the file.** Use commands such as `hermes moa list` and `hermes config check`.
4. Once a reversible config change is authorized, execute it. Do not re-ask permission in a loop. Ask again only for genuinely new risk such as destructive changes, credentials, or network actions.

## Edit Pathways

### 1. Domain subcommands

Preferred whenever available:

```bash
hermes moa configure
hermes model ...
```

### 2. Scripted `EDITOR`

For precise non-interactive edits that respect config protection, use a temporary editor script and invoke:

```bash
EDITOR=/path/to/script.py hermes config edit
```

Use surgical text insertion rather than fully re-dumping YAML, which can mangle multi-line personality values. For an exact replacement, write the old and new YAML blocks to temporary files and use the supported editor pathway.

### 3. `hermes config set`

Useful for simple scalars and existing nested keys:

```bash
hermes config set <key> <value>
```

Do not use it to append to a list by numeric index. An out-of-range index can raise `IndexError` while misleadingly exiting with status 0. Build the full structure via scripted `EDITOR` instead.

## MoA Named-Preset Schema

`hermes moa list` reads from `moa.presets.<name>`, not the flat top-level `moa.reference_models`. When presets exist, the flat block is only a compatibility view and edits to it may be silently ignored.

Use the preset structure:

```yaml
moa:
  default_preset: default
  active_preset: ''
  presets:
    default:
      reference_models:
      - provider: openai-codex
        model: gpt-5.5
      - provider: openrouter
        model: moonshotai/kimi-k2
      aggregator:
        provider: openrouter
        model: anthropic/claude-opus-4.8
      reference_temperature: 0.6
      aggregator_temperature: 0.4
      max_tokens: 4096
      enabled: true
```

`active_preset: ''` means MoA runs only on explicit `/moa <prompt>` commands, not every message.

## Provider Model Slugs

Marketing or UI version strings are not necessarily API model slugs. A stored slug being accepted by `hermes moa list` only proves Hermes saved it, not that the provider accepts it at runtime. Verify with a real runtime call such as one `/moa <prompt>` or with the provider catalog before claiming success.

## MCP OAuth Callback Timeout

If `hermes mcp login` expires after roughly 40 seconds even though the server is configured correctly, do not repeatedly retry the same CLI path. The login wrapper may not pass the server's configured `connect_timeout` through to its probe. Use Hermes' internal `_probe_single_server(..., connect_timeout=300)` from a temporary interactive-PTY script, then verify with:

```bash
hermes mcp test <server>
```

Also check the cached OAuth token. Token presence alone is not successful integration: confirm tool discovery and the discovered-tool count.

If discovery fails with an `httpx` Brotli decoding error after the token is present, add a per-server header through the supported config editor pathway, after backing up the config:

```yaml
headers:
  Accept-Encoding: gzip, deflate
```

This prevents Hermes/httpx from advertising Brotli while retaining gzip/deflate.

## Known Failures

- `patch`/`write_file` on `config.yaml` refuses with a message directing you to `hermes config`. This is expected; use a supported pathway.
- `hermes config set moa.reference_models.2.provider ...` can fail when index 2 does not exist. Use the full preset structure via scripted `EDITOR`.
- `hermes config set mcp_servers.super-browser.env.BROWSER_USE_API_KEY ...` can fail with `ValueError: Invalid environment variable name`. Nested MCP environment keys cannot be set this way. Use the scripted `EDITOR` pathway, then restart the MCP server so it picks up new environment variables:
  ```bash
  hermes mcp remove super-browser
  hermes mcp add super-browser --command ... --env KEY=VALUE ...
  ```

## Verification Checklist

- [ ] Backup created before editing.
- [ ] Preferred domain subcommand used where available.
- [ ] Smallest possible change applied through a supported pathway.
- [ ] Correct named-preset schema used for MoA.
- [ ] Model slugs verified against a provider or real runtime call.
- [ ] `hermes config check` or the relevant domain command passes.
- [ ] MCP changes verified with `hermes mcp test <server>` and discovered tools, not token presence alone.
- [ ] MCP server restarted after changing its environment variables.
