# Higgsfield setup and authentication handoff

## What happened in the pilot setup

- `npm i -g @higgsfield/cli` completed successfully.
- The installed executable was at `/opt/data/home/.npm-global/bin/higgsfield`, which was not on the shell PATH in one invocation. Export the npm global bin path before calling it.
- `higgsfield auth login` opened the OAuth flow and waited for browser approval.
- The browser approval flow reached Higgsfield sign-in, but authentication was not completed in the session.
- `npx skills add higgsfield-ai/skills` cloned the repository and found seven skills, then stopped at an interactive selection prompt. This is not a completed install.

## Reliable verification sequence

```bash
npm i -g @higgsfield/cli
export PATH="$HOME/.npm-global/bin:$PATH"
higgsfield account status
```

If unauthenticated:

```bash
higgsfield auth login
# Complete the browser approval, then:
higgsfield account status
higgsfield model list --json
```

For companion skills, avoid leaving the installer at an interactive prompt. Check the local CLI help, then use the supported non-interactive/global flags. Expected form:

```bash
npx skills add higgsfield-ai/skills --yes --global
```

Verify the result rather than trusting the command’s initial clone message.

## Pitfalls

- `higgsfield: command not found` can mean the npm global bin directory is missing from PATH, not that installation failed.
- A browser URL being opened does not mean authentication succeeded.
- A cloned skill repository is not the same as installed skills.
- Do not generate newsletter assets until both account status and model discovery succeed.
