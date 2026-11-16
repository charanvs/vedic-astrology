# Step 14 release checklist

| Control | Status | Evidence / blocker |
|---|---|---|
| Registration/login/logout | PASS | backend integration tests |
| Argon2id password storage | PASS | PHC hash and verify tests |
| Verification/recovery token lifecycle | PASS | expiry/single-use logic tested locally |
| Live SMTP delivery | BLOCKED | credentials/provider not supplied |
| Server sessions/cookies/CSRF | PASS | local + production-config tests |
| Object authorization | PASS | synthetic User A/User B tests |
| Legacy ownership recovery | BLOCKED | four profiles quarantined pending identity review |
| Roles | PASS | registration fixed to user; local admin procedure |
| Account export/deletion request | PASS | authenticated scoped endpoints; deletion is a request workflow |
| Rate limiting | PASS | MySQL-backed auth/PDF limits; production load test pending |
| CORS/security headers | PASS | restricted config/header tests |
| Dependency vulnerability scans | PASS | pip-audit and npm audit: zero known findings |
| Database migration/data preservation | PASS | revision 20261115_01; 4/4 profiles preserved |
| Backup creation/readability | PASS | dump contains schema and profile rows |
| Isolated restore | PASS | disposable DB restored, checked, and removed |
| Backend/frontend regressions | PASS | see latest test report |
| Production React base path | PASS | production build |
| GoDaddy startup/proxy/native libs | BLOCKED | staging access deferred to Step 15 |
| HTTPS/HSTS through production proxy | NOT TESTED | production not accessed |
| Swiss Ephemeris license | BLOCKED | AGPL vs professional decision required |
| AI security/quotas | BLOCKED | Step 13 AI feature is absent |
| DPDP/legal review | BLOCKED | counsel/process review required |

Rollback: retain the pre-migration SQL dump and previous assets; stop traffic, restore only through an approved database recovery plan, deploy the previous application build, validate health, and rotate secrets if compromise is involved. Alembic downgrade drops security tables and columns and must not be used casually because it destroys authentication state.
