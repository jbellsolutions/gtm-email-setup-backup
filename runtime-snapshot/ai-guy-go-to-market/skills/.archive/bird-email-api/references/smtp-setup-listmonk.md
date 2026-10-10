# Bird SMTP → ListMonk Migration Procedure

This file documents the planned migration of ListMonk's SMTP from Resend to Bird's SparkPost SMTP relay. As of Jul 27 2026, this has NOT been executed — Bird's email product is not yet fully provisioned.

## Prerequisites (all must be true before starting)

1. Bird email product is activated (DKIM generates, default domains show healthy)
2. A `bk_eu1_` API key exists with "Send via SMTP" permission
3. `send.usingaitoscale.com` is added as a sending domain in Bird
4. All 4 DNS records are published at Hostinger:
   - Bounce CNAME: `bounce.send.usingaitoscale.com` → `eu.sparkpostmail.com`
   - Tracking CNAME: `track.send.usingaitoscale.com` → `v2.spgo.io`
   - DKIM TXT/CNAME: (Bird generates this once email is activated)
   - DMARC TXT: `_dmarc.send.usingaitoscale.com` → `v=DMARC1; p=none;`
5. Domain verification passes in Bird dashboard

## Migration Steps

### 1. Get SMTP credentials from Bird

The SMTP password is the Bird API key with "Send via SMTP" permission. Create it at:
- Bird dashboard → Developers → API Keys → Create new key
- Select "Send via SMTP" scope
- Copy the key (starts with `bk_eu1_`)

### 2. Update ListMonk SMTP settings

Log in to ListMonk admin → Settings → SMTP tab, change:

| Field | Old (Resend) | New (Bird) |
|---|---|---|
| Host | `smtp.resend.com` | `smtp.eu.sparkpostmail.com` |
| Port | 465 | 587 |
| TLS | SSL/TLS | STARTTLS |
| Username | `resend` | `SMTP_Injection` |
| Password | (Resend key) | `bk_eu1_...` (Bird API key) |
| Max connections | 2 | 2 |
| Idle timeout | 15s | 15s |
| Wait timeout | 10s | 10s |

Click Save.

### 3. Verify via API

```javascript
// In browser console on ListMonk admin:
fetch('/api/settings').then(r => r.json()).then(d => {
  const smtp = d.data.smtp[0];
  console.log(`Host: ${smtp.host}, Port: ${smtp.port}, Enabled: ${smtp.enabled}`);
})
```

### 4. Send mail-tester test

1. Go to mail-tester.com, get a fresh test address
2. In ListMonk, create a test list + add mail-tester address as subscriber
3. Create a simple test campaign targeting that list
4. Start the campaign
5. Check `/api/logs` for errors
6. Check mail-tester.com for the score

### 5. Update ListMonk default from email

The from email `Justin <justin@send.usingaitoscale.com>` should work with Bird if the domain is verified. If Bird requires a different from address, update in Settings → General → Default `from` email.

### 6. Rollback (if needed)

If Bird SMTP fails, revert to Resend settings:
- Host: `smtp.resend.com`, Port: 465, TLS: SSL/TLS, Username: `resend`
- BUT Resend domain is also not verified, so rollback only helps if Resend domain gets verified too.

## Bird Account State (Jul 27 2026)

- Workspace UUID: `2a6e327b-190a-4505-9764-4397353b0cf8`
- Channel ID for send.usingaitoscale.com: `cf828b31-6316-5d22-a150-ac3168c30821`
- Region: EU
- API key: `[REDACTED]` (LEGACY — no email permissions, needs replacement)
- Email product: NOT PROVISIONED (DKIM won't generate, all email API endpoints return 401)
- 3 of 4 DNS records obtained from dashboard, DKIM blocked by provisioning issue