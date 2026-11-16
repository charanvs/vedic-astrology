# Vedic Astrology

Foundation for a modern Vedic Astrology web application focused on traditional Indian Jyotish. Version 1.2.0 adds registered-user authentication, private profile ownership, server-managed sessions, CSRF protection, account privacy controls, and deployment security preparation. It provides calculated traditional classifications, not scientific predictions.

Live deployment: https://cvstudy.in/astrology. To build the deployment pack run `.venv\Scripts\python.exe deploy\build_release.py` in `backend`; installation steps are in `docs/DEPLOYMENT_GODADDY.md`.

## License

Copyright (C) 2026 cvstudy.in.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. It is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; see the `LICENSE` file for details.

Planetary calculations use the Swiss Ephemeris (Free Edition, AGPL) by Astrodienst AG. Bundled Noto fonts are under the SIL Open Font License 1.1; city data is from GeoNames under CC BY 4.0. Details are in `THIRD_PARTY_NOTICES.md`.

## Technology stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, Axios, Lucide React
- Backend: Python, FastAPI, Pydantic, Uvicorn, SQLAlchemy 2, Alembic, PyMySQL
- Security: Argon2id password hashes, opaque HttpOnly sessions, synchronizer CSRF tokens, MySQL-backed rate limits
- Testing: Vitest, React Testing Library, Pytest, HTTPX
- Database: MySQL 8.4 on WAMPServer port 3306
- Astronomy: `pyswisseph` Python binding for Swiss Ephemeris (Python 3.11 required on Windows)

## Database setup

MySQL must be running locally. Copy `backend/.env.example` to the ignored `backend/.env` and provide separate runtime, migration, and test credentials. Never place credentials in frontend variables or Git.

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\backend
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Create a migration with `python -m alembic revision --autogenerate -m "description"`, inspect it before applying, and use `python -m alembic downgrade -1` only after reviewing data-loss risk. See `docs/DATABASE_SETUP.md`.

## Project location

`C:\wamp64\www\Projects\vedic-astrology`

## Backend

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: `http://127.0.0.1:8000/docs`

## Frontend

Open a second PowerShell terminal:

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\frontend
npm.cmd run dev
```

Application: `http://localhost:5173/` (the server binds to the local loopback interface).

The interface includes registration/login/recovery/account pages, persisted themes, private searchable profiles, verified birthplace autocomplete, accessible North Indian charts, Planetary Positions, Daily Panchang, Vimshottari Dasha, Ashtakoota Matching, D1/D9/D10, and PDF reports. See `docs/AUTHENTICATION.md`, `docs/AUTHORIZATION.md`, and `docs/RELEASE_CHECKLIST.md`.

## Testing and builds

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\backend
.\.venv\Scripts\python.exe -m pytest

cd C:\wamp64\www\Projects\vedic-astrology\frontend
npm.cmd run test
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

The production build uses `/vedic-astrology/` for asset paths. Future hosting must send direct client-side routes back to `index.html`.

## Local URLs

- Frontend: `http://localhost:5173/`
- API documentation: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`
- Version: `http://127.0.0.1:8000/api/version`
- Database health: `http://127.0.0.1:8000/api/db-health`
- Locations: `http://127.0.0.1:8000/api/locations`
- Birth profiles: `http://127.0.0.1:8000/api/birth-profiles`
- Birth-time validation: `http://127.0.0.1:8000/api/birth-time/validate`
- Astrology metadata: `http://127.0.0.1:8000/api/astrology/config`
- Saved-profile calculation: `http://127.0.0.1:8000/api/astrology/birth-profiles/{id}/calculate`
- Daily Panchang UI: `http://localhost:5173/panchang`
- Stored-location Panchang: `http://127.0.0.1:8000/api/panchang/daily?date=2026-11-13&location_id={id}`
- Coordinate Panchang: `http://127.0.0.1:8000/api/panchang/calculate`
- Panchang configuration: `http://127.0.0.1:8000/api/panchang/config`
- Vimshottari Dasha UI: `http://localhost:5173/dasha`
- Dasha configuration: `http://127.0.0.1:8000/api/dasha/config`
- Ad-hoc Dasha calculation: `http://127.0.0.1:8000/api/dasha/calculate`
- Saved-profile Dasha: `http://127.0.0.1:8000/api/dasha/birth-profiles/{id}`
- Current saved-profile Dasha: `http://127.0.0.1:8000/api/dasha/birth-profiles/{id}/current`
- Kundli Matching UI: `http://localhost:5173/matching`
- Matching configuration: `http://127.0.0.1:8000/api/matching/config`
- Matching rule metadata: `http://127.0.0.1:8000/api/matching/rules`
- Match saved profiles: `POST http://127.0.0.1:8000/api/matching/birth-profiles`
- Divisional Charts UI: `http://localhost:5173/divisional-charts`
- Divisional configuration: `http://127.0.0.1:8000/api/divisional/config`
- Ad-hoc D9/D10 calculation: `POST http://127.0.0.1:8000/api/divisional/calculate`
- Saved-profile D9: `http://127.0.0.1:8000/api/divisional/birth-profiles/{id}/d9`
- Saved-profile D10: `http://127.0.0.1:8000/api/divisional/birth-profiles/{id}/d10`
- PDF Reports UI: `http://localhost:5173/reports`
- Report configuration: `http://127.0.0.1:8000/api/reports/config`
- Kundli PDF: `POST http://127.0.0.1:8000/api/reports/kundli`
- PDF preview: `POST http://127.0.0.1:8000/api/reports/preview`
- Matching PDF: `POST http://127.0.0.1:8000/api/reports/matching`
- Planned production: `https://cvstudy.in/vedic-astrology/`

## Troubleshooting

- Use `npm.cmd` when PowerShell execution policy blocks `npm.ps1`.
- If `oxlint` reports that Windows Application Control blocked its native binding, the source can still be checked with `npm.cmd run typecheck`, tests, and the production build; resolve the machine policy before relying on lint locally.
- Start the backend before the frontend to see **Backend Connected** immediately.
- If the dashboard shows **Backend Unavailable**, verify port 8000 and visit the health URL directly.
- Do not stop unrelated applications to free ports; use an alternate port and update configuration.
- GoDaddy's Python startup and subpath proxy arrangement must be verified before deployment.
- Python 3.14 cannot install the selected binding from a wheel. The validated Windows runtime is Python 3.11.
- Public activation is blocked until either the whole project satisfies AGPLv3 obligations or a Swiss Ephemeris Professional License is obtained.
- Birth-profile and saved-calculation APIs require an authenticated owner. Four historical unowned profiles remain quarantined until the controlled claim procedure is used.
- Development registration/recovery responses include a mail-sink token; production suppresses it and requires configured SMTP.
- Do not expose the service publicly until all BLOCKED items in `docs/RELEASE_CHECKLIST.md` are resolved.
