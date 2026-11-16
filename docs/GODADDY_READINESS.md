# GoDaddy readiness assessment

GoDaddy documentation confirms Python and MySQL are available on applicable hosting plans, but that does not confirm this account's Python version, ASGI support, Passenger adapter, native libraries, outbound SMTP/AI access, or resource limits. Official component matrix: https://www.godaddy.com/help/which-components-does-my-hosting-support-5614

Required verification on staging, not Step 14:

1. Python 3.11 (required by the validated pyswisseph wheel).
2. Whether Passenger/cPanel invokes WSGI only. FastAPI is ASGI; use a verified supported ASGI server or a tested adapter. Do not invent `passenger_wsgi.py`.
3. Proxy mount of API and SPA at `/vedic-astrology/`, direct-route fallback, and forwarded scheme/host behavior.
4. MySQL 8-compatible credentials and restricted runtime grants.
5. Installation/import of pyswisseph, cryptography Argon2id, WeasyPrint, Pango/HarfBuzz, and bundled Unicode fonts.
6. Private writable temporary/log paths and worker memory/CPU limits.
7. Secure cookie path and HTTPS behavior through the proxy.
8. SMTP TLS and outbound provider connectivity.
9. Future AI provider egress, timeouts, quotas, privacy and key injection (AI is not present now).
10. Backup/restore, error log, restart, health check, rollback, and static asset deployment.

React already builds with Vite base `/vedic-astrology/` and Router derives the same basename. Public deployment is blocked pending staging verification.

Swiss Ephemeris is dual licensed; choose AGPL-compatible publication or purchase/execute the professional license before activating a public service. Official terms: https://www.astro.com/swisseph/swephinfo_h.htm
