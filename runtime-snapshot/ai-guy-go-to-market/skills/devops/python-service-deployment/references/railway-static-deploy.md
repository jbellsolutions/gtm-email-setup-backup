# Railway exact-as-is static Python deployment

## Command sequence

```bash
npx @railway/cli login
npx @railway/cli whoami
npx @railway/cli project list
npx @railway/cli link --project <project> --environment production
npx @railway/cli add --service <service> --json
npx @railway/cli up /path/to/extracted --path-as-root \
  --service <service> --environment production --detach --yes --json
npx @railway/cli deployment list --json
npx @railway/cli domain --service <service> --json
```

`--path-as-root` is essential when the upload argument is a directory. Without it, the archive can contain the extraction directory as a top-level folder, so Railpack sees no `requirements.txt`, `Procfile`, or Python entrypoint.

## Verification checklist

Use an HTTP client that does not follow redirects automatically:

- Assert each clean route returns HTTP 200.
- Assert each legacy filename returns HTTP 301 and the exact clean-route `Location`.
- Extract iframe URLs from the deployed landing page and request them separately.
- For exact-as-is HTML, compare SHA-256 and byte length of every deployed page response to its ZIP member.
- Poll deployment status to `SUCCESS` and inspect build logs for Python detection, Procfile discovery, and Gunicorn binding to `$PORT`.

Do not claim success from an upload ID alone. The final evidence is a successful deployment plus live HTTP verification.
