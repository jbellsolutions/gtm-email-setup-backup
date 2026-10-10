---
name: slack-cli
description: Use when operating Slack via the official CLI.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [slack, slack-cli, apps, agents, workspace-automation]
    related_skills: [hermes-agent, native-mcp]
---

# Slack CLI

## Overview

The official Slack CLI creates and manages Slack apps from the terminal. It supports AI Agent app scaffolding, app installation and deployment, direct Slack Web API calls, triggers, datastores, collaborators, auth, and developer sandboxes.

The binary is installed at `~/.slack/bin/slack`, with the `slack` command linked into the user's local bin directory. Verify availability before use:

```bash
slack --version
slack doctor
```

Treat the live CLI help as authoritative because commands and flags can change:

```bash
slack --help
slack <command> <subcommand> --help
```

## When to Use

Use this skill when the user asks to:

- Create an AI Agent app in Slack: `slack create agent <name>`
- Create or initialize a Slack app project
- Authenticate the CLI or inspect authorized accounts
- Deploy, install, uninstall, link, or delete a Slack app
- Call Slack Web API methods from the terminal
- Create or manage triggers, datastores, collaborators, sandboxes, or app functions
- Diagnose Slack CLI, app, or authentication issues

Do not claim that a Slack action succeeded until the command returns success and the result is verified. Do not use a user token or bot token unless the user has authorized that scope and operation.

## Authentication

Check auth state first:

```bash
slack auth list
slack doctor
```

For interactive authorization, run:

```bash
slack login
```

The user must complete the browser/device authorization flow when prompted. For non-interactive environments, Slack supports pre-authenticated login using a ticket/challenge or an explicitly supplied token; never place tokens in shell history, skill files, source code, or chat output.

Useful auth commands:

```bash
slack auth list
slack auth login --help
slack auth logout
slack auth revoke --help
```

If an operation concerns a specific workspace, pass `--team <team-id-or-name>` where supported. Use `slack auth list` rather than guessing the workspace.

## Create an AI Agent App

Create a local project only after confirming the requested name and destination. From the intended parent directory:

```bash
slack create agent <agent-name>
```

Inspect the generated project before running or deploying it. Use:

```bash
slack manifest info
slack manifest validate
slack project init --help
```

Runtime dependencies are not installed by the Slack CLI automatically. Identify the generated runtime and follow its project instructions before local execution.

## App Lifecycle

Common commands:

```bash
slack project create <name>
slack project init
slack app link
slack app install
slack platform run
slack platform deploy
slack app list
slack app settings
slack app uninstall
slack app delete
```

Deployment and installation can create external Slack resources or change an existing app. Confirm scope before destructive operations such as deleting an app, uninstalling it, revoking auth, or removing collaborators.

## Direct Slack API Calls

Use `slack api <method>` for authorized Web API operations:

```bash
slack api auth.test
slack api conversations.list
slack api users.list
slack api chat.postMessage --json '{"channel":"C...","text":"..."}'
```

Token resolution is: explicit `--token`, linked app via `--app`, `SLACK_BOT_TOKEN`, `SLACK_USER_TOKEN`, then an app prompt in a project. Prefer a linked app or CLI-managed auth. Never print or expose token values.

For read operations, fetch and inspect the returned JSON. For writes, capture the returned `ok`, resource ID, timestamp, or equivalent confirmation, then perform a read-back when practical. Use `--include` when HTTP status or headers are needed.

Examples:

```bash
slack api conversations.info channel=C0123456789
slack api reactions.add channel=C0123456789 timestamp=1234567890.123456 name=thumbsup
slack api blocks.validate --no-auth blocks='[{"type":"section","text":{"type":"mrkdwn","text":"Hello"}}]'
```

Do not guess channel IDs, user IDs, app IDs, timestamps, scopes, or trigger IDs. Discover them with the appropriate read command or require them from the user.

## Triggers, Datastores, and Sandboxes

Inspect command help before acting:

```bash
slack trigger list
slack trigger create --help
slack datastore query --help
slack sandbox list
```

Treat trigger creation, datastore writes, sandbox creation, and collaborator changes as external side effects. Verify the returned identifier and configuration after creation.

## Safety and Secrets

- Authorization is separate from installation. A logged-in CLI does not imply permission to deploy or modify every workspace.
- Never pass secrets through URLs, commit them, write them into skills, or include them in final responses.
- Prefer `--json` for structured API bodies and validate JSON locally before sending.
- Use read-only discovery first: `auth list`, `doctor`, `app list`, `manifest info`, `trigger list`, or the relevant Slack API read method.
- Do not send messages, create channels, install apps, deploy apps, alter permissions, or delete resources unless the user's request clearly authorizes that action.
- In shared Slack threads, do not infer a target user or channel from unverified historical mentions. Use IDs supplied in the current request or discover them through authorized CLI reads.

## Troubleshooting

1. Run `slack --version` and `slack doctor`.
2. If credentials fail, run `slack auth list`, then `slack login` interactively.
3. If a command is unclear, run its exact `--help` command.
4. Check the CLI debug log path reported by the command, commonly `~/.slack/logs/`.
5. Validate app manifests before deployment.
6. For `not_authed`, do not retry API writes. Re-authenticate first.

## Verification Checklist

- [ ] `slack --version` succeeds.
- [ ] `slack doctor` reports CLI and system readiness.
- [ ] Authentication is checked with `slack auth list` before workspace operations.
- [ ] The requested project/app/resource name and scope are explicit.
- [ ] Any generated project is inspected and its manifest validates.
- [ ] External writes return a success flag and an ID/timestamp where applicable.
- [ ] Destructive operations are confirmed by scope and verified afterward.
- [ ] No credentials appear in files, logs copied into chat, or the final response.
