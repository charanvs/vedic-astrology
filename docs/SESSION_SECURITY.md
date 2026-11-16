# Session security

The browser receives only a high-entropy opaque `vedic_session` cookie. The database stores its SHA-256 verifier, a separate CSRF verifier, user ID, timestamps, revocation, hashed client IP, and a truncated user-agent. Session secrets are never logged or returned after login.

- Idle timeout: 30 minutes by default.
- Absolute timeout: 24 hours by default.
- Login creates a new session; no pre-authentication ID is reused.
- Logout revokes the server row and expires the cookie.
- Password reset revokes every session.
- Password change revokes other sessions.
- Users can list safe session metadata and revoke only their own sessions.

Local HTTP uses `HttpOnly; SameSite=Lax; Path=/` without Secure. Production requires `Secure=true` and uses `Path=/vedic-astrology/` to isolate this app. No Domain attribute is set. A `__Host-` name is intentionally not used because it would require `Path=/`.

HTTPS is mandatory in production. See OWASP session guidance: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
