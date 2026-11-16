# Account privacy and retention

Stored data can include identity/contact data, exact birth data, places, charts derived on demand, and report content. The application minimizes storage: calculated charts and generated PDF bytes are not persisted by Step 14.

`GET /api/account/export` returns only the authenticated account and owned profiles as JSON; it excludes password hashes, token verifiers, sessions, audit internals, and other users. `POST /api/account/deletion-request` requires the current password and exact confirmation phrase, records the request, and does not irreversibly delete data. An operator must verify the request, define handling of owned profiles, execute the approved procedure, and record backup-retention effects.

Proposed retention before launch:

- revoked/expired sessions and account tokens: purge after 30 days;
- security audit events: 180 days unless an incident requires a hold;
- generated PDFs: response-only temporary memory, no public storage;
- account data: until deletion is approved or the stated service purpose ends;
- encrypted backups: 30-day rolling retention, with deletion aging out through rotation.

India's DPDP Rules 2025 have phased commencement dates; legal review is required before launch and this document is not a compliance claim. Official notification: https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa
