# Production configuration

Start from `backend/.env.production.example`; create the actual file outside Git with restrictive ACLs. Required secret values are database, SMTP, and any future AI provider credentials. React receives only `VITE_API_BASE_URL=/vedic-astrology/`; never expose secrets through `VITE_*`.

Production invariants:

- `APP_ENV=production`, docs disabled;
- public/base path exactly `https://cvstudy.in/vedic-astrology` and `/vedic-astrology`;
- CORS origin exactly `https://cvstudy.in` (origins have no path);
- trusted hosts limited to cvstudy.in names;
- Secure HttpOnly SameSite=Lax cookie scoped to `/vedic-astrology/`;
- TLS terminated only by a trusted proxy and authenticated traffic never downgraded;
- dedicated least-privilege MySQL runtime account;
- SMTP TLS and verified sender;
- writable private temp/log locations outside public_html;
- explicit Swiss ephemeris/font/native PDF paths.

Rotate a secret by provisioning its replacement, updating the external environment, restarting workers, validating health/auth, and revoking the prior credential. Database rotation should overlap grants briefly. SMTP/API keys should be revoked at the provider after successful validation. Session tokens are random per login; revoke all rows if session-store disclosure is suspected.

Do not trust arbitrary forwarded headers. Configure trusted proxy handling only after the actual GoDaddy proxy chain is known.
