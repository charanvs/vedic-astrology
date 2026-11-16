# Step 14 security audit

Baseline: 236 backend and 65 frontend tests passed before change. Authentication did not exist; all profile CRUD was public, personal calculations relied only on development mode, CORS did not support credentialed writes, and there was no CSRF, rate limiting, audit trail, recovery, or account workflow.

| Finding | Severity | Component | Remediation | Verification | Remaining risk |
|---|---|---|---|---|---|
| Anonymous profile disclosure/write | Critical | profile APIs | session auth, server owner assignment/filter | cross-user and anonymous tests | legacy profiles require claim |
| IDOR in saved calculations/PDF | High | D1/Dasha/D9/D10/matching/reports | ownership filter before calculation | two-user integration tests | audit new endpoints |
| No password/session system | Critical | application | Argon2id, opaque hashed sessions, expiry/revocation | auth lifecycle tests | SMTP not live-tested |
| CSRF exposure | High | writes | synchronizer token + Origin validation | missing/invalid/cross-origin tests | reverse-proxy origin must be verified |
| Brute-force/automation | High | auth/PDF | MySQL-backed window counters | HTTP 429 tests | cleanup job/production concurrency load test |
| Weak response hardening | Medium | HTTP | CSP, nosniff, referrer, permissions, production HSTS | header tests | CSP must be tested through GoDaddy proxy |
| Vulnerable PDF dependencies | High | pypdf/pdfminer | upgraded pypdf 6.21.4, pdfplumber 0.11.10, pdfminer-six 20260107 | pip-audit: no known vulnerabilities; PDF tests pass | monitor advisories |
| Unowned historical profiles | High | database | private quarantine + audited CLI claim | count remains four | operator identity verification |
| Live mail absent | High | verification/recovery | SMTP adapter and safe dev sink | token lifecycle tests | provider/delivery test blocked |
| AI milestone absent | High | AI | no AI routes or keys exposed | code inventory | Step 13 functionality unavailable |
| Swiss Ephemeris licensing undecided | High | production | release gate retained | documentation review | choose AGPL-compatible release or professional license |
| GoDaddy runtime unknown | High | hosting | compatibility checklist | local only | verify ASGI/WSGI adapter, native libraries, filesystem |

No known Critical finding remains in the implemented local surface. High findings above are release blockers. Source review follows OWASP Password Storage, Authentication, Session Management, CSRF, and HTML5 Security cheat sheets.
