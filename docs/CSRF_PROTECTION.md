# CSRF protection

Authenticated state-changing requests use a synchronizer token. Login returns a random token kept only in React memory. A page refresh obtains a newly rotated token from `GET /api/auth/csrf` after the HttpOnly session is validated. Axios sends it as `X-CSRF-Token`.

The server compares the SHA-256 verifier in constant time. Missing/invalid tokens return 403. If an Origin header is present it must match the configured allowlist, providing an additional cross-origin check. SameSite=Lax is defense in depth, not the primary control.

Protected operations include logout, password/account changes, location/profile writes, matching, and PDF generation. Registration, login, verification, and recovery use no ambient authenticated authority and are separately rate-limited.

Never place the CSRF or session token in localStorage. After a 401, private client state must be discarded and the user returned to login.
