# Separate-Account Handoff Package Checklist

Use this reference when exporting an outbound operating system for a different team or account.

## Required artifacts

1. Skills with focused triggers and class-level procedures.
2. System/operating contract for the receiving agent.
3. End-to-end workflow with decision and stop gates.
4. Human handoff/setup document.
5. Copy-paste agent instructions.
6. Starter scripts/templates where they reduce hand-typed API work.

## Sanitization rules

Exclude credentials, bearer tokens, API keys, account IDs, campaign IDs, internal paths, private lead/customer data, organization-specific metrics, private case studies, and assumptions about the recipient's plan or platform state. Use placeholders and clearly identify what the recipient must supply.

## Evidence boundaries

Documentation transfer proves only that files were produced. It does not prove access to, configuration of, lead import into, rendering in, activation of, or delivery from the receiving account. Label each as unverified until exercised against that account.

## Safe implementation order

1. Validate package structure and frontmatter.
2. Run scripts against fixtures.
3. Scan for credential-like strings and private identifiers.
4. Archive and checksum the package.
5. Recipient performs read-only discovery using its own credentials.
6. Recipient creates a paused test campaign and reconciles a tiny test import.
7. Recipient previews rendered copy.
8. Human owner approves activation separately from copy or import approval.

## Handoff acceptance criteria

The recipient can identify which account is in scope, configure its own secrets, run read-only discovery, explain the source/suppression/verification gates, build a paused test, reconcile counts, inspect rendering, and identify the exact human approval required before activation or replies.
