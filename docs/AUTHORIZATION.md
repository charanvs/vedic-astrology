# Authorization

The backend is deny-by-default for saved personal data. React route guards improve navigation only; FastAPI independently verifies every request.

| Resource | Anonymous | User | Admin |
|---|---:|---:|---:|
| Health, public configuration, public Panchang | Read | Read | Read |
| Locations | Search/read | Create/update | Create/update |
| Birth profiles | No | Own only | Own only (no implicit global access) |
| Saved D1/Dasha/D9/D10 | No | Own only | Own only |
| Saved-profile matching | No | Both profiles must be owned | Same |
| PDF preview/download | No | Every referenced profile must be owned | Same |
| Account/sessions/export | No | Own only | Own only |

Profile ownership is assigned from the authenticated session; `user_id` is rejected as an extra create field. Non-owned and unowned identifiers return 404 to avoid disclosing existence.

Four pre-Step-14 profiles are currently unowned and quarantined. They were not deleted or assigned. After independent identity verification, run a dry run and then explicitly apply:

```powershell
.\.venv\Scripts\python.exe scripts\claim_unowned_profiles.py --email owner@example.com --profile-id 1
.\.venv\Scripts\python.exe scripts\claim_unowned_profiles.py --email owner@example.com --profile-id 1 --apply
```

Administrative status does not grant broad profile access. New privileged endpoints must explicitly depend on `require_admin`, document their purpose, and add denial tests.

## Account approval

With `REQUIRE_ADMIN_APPROVAL=true` (the default), a self-registered account cannot sign in until an administrator approves it. The check runs both at login and on every authenticated request, so an existing session stops working if approval is missing. Administrators are always treated as approved.

Administrators manage accounts at `/admin` in the frontend, backed by these endpoints (all require the `admin` role; state changes also require CSRF):

| Endpoint | Purpose |
| --- | --- |
| `GET /api/admin/summary` | Counts of pending, approved, deactivated and all accounts |
| `GET /api/admin/users?status=pending\|approved\|inactive\|all` | List accounts by status |
| `POST /api/admin/users/{id}/approve` | Approve a pending account (records who approved it and when) |
| `POST /api/admin/users/{id}/deactivate` | Disable sign-in and revoke all sessions |
| `POST /api/admin/users/{id}/reactivate` | Restore a deactivated account |

Administrators cannot deactivate themselves or other administrators from the dashboard. Every change is written to `audit_events`. Administrator access is granted only from the command line, as a dry run first:

```powershell
.\.venv\Scripts\python.exe -m scripts.grant_admin --email owner@example.com
.\.venv\Scripts\python.exe -m scripts.grant_admin --email owner@example.com --apply
```
