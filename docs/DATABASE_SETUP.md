# Database Setup

## Local discovery

- Engine: MySQL Community Server 8.4.7 (not MariaDB)
- WAMP installation: `C:\wamp64\bin\mysql\mysql8.4.7`
- Host and port: `127.0.0.1:3306`
- Service: `wampmysqld64`
- Development schema: `vedic_astrology`
- Test schema: `vedic_astrology_test`

Both schemas use `utf8mb4` and `utf8mb4_unicode_ci`. MariaDB 11.4.9 is separately installed on port 3307 and is not used.

## Accounts and credentials

Local accounts are hostname-restricted and separated by purpose:

- `vedic_app`: runtime SELECT, INSERT, and UPDATE on the development schema.
- `vedic_migrator`: schema migration and development maintenance privileges.
- `vedic_test`: privileges only on the isolated test schema.

Actual passwords live in ignored environment files. `.env.example` contains placeholders only. The temporary `.env.mysql-admin` setup credential must never be committed and can be removed after provisioning if no longer needed.

## Initial schema

The initial migration creates `users`, `locations`, and `birth_profiles`, plus `alembic_version`. Tables use InnoDB, foreign keys, utf8mb4, coordinate constraints, a known-time constraint, and query indexes. Birth time remains the entered local time; later calculations must combine it with the location's IANA timezone.

## Alembic commands

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\backend
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "change description"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Review every generated migration. Use `downgrade -1` only when its destructive impact is understood and acceptable.

## Test isolation

Pytest connects only to `vedic_astrology_test`, cleans its own synthetic rows, and never deletes development data. Set `ALEMBIC_USE_TEST_DB=1` only when applying or checking migrations against the test schema.

## Troubleshooting

- Confirm MySQL listens on 3306 and MariaDB is not selected accidentally.
- Run `/api/db-health`; it returns HTTP 503 without exposing connection details when unavailable.
- Verify the migration with `alembic current`.
- Check that passwords with special characters are individual environment values; SQLAlchemy `URL.create()` performs safe encoding.

## Production portability

GoDaddy must receive separate production credentials, an external hostname if required, and a reviewed migration workflow. Remote MySQL availability, FastAPI process startup, and subpath proxying must be verified before deployment. Never reuse local or test credentials in production.
