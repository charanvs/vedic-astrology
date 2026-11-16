# Authentication

Version 1.2 uses email/password authentication and opaque server-managed sessions. Passwords are hashed with Argon2id through the maintained `cryptography` package using OWASP's minimum profile: 19 MiB, two iterations, one lane, 32-byte output, and a random 16-byte salt. Passwords are 12–128 characters; pasting and password managers are supported.

Endpoints are `POST /api/auth/register`, `verify-email`, `resend-verification`, `login`, `logout`, `forgot-password`, `reset-password`, and `change-password`; session/account reads are under `GET /api/auth/*` and `/api/account/*`. Public registration always assigns `user`. Login requires an active, verified account.

Verification and reset tokens are 48-byte URL-safe random values. Only SHA-256 verifiers are stored, tokens expire, and successful use is single-use. Development returns a token as a mail-sink aid. Production never returns it and requires SMTP. Live SMTP delivery is not yet tested.

Provision an administrator only from a local development shell:

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\backend
.\.venv\Scripts\python.exe scripts\provision_admin.py --email operator@example.com --name "Operator"
```

The password is read twice without a command-line argument. Verification is still required. Never run this against production during Step 14.

Reference: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
