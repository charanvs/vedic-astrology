# Birth Profile and Location Management

## Scope

Step 5 captures accurate input data for later Swiss Ephemeris calculations. It does not calculate a Kundli, Julian day, planets, Lagna, Rashi, Nakshatra, Panchang, Dasha, matching, or predictions. The module is local-development-only until authentication and authorization exist.

## Birth-profile fields

- `full_name`: required Unicode text, maximum 150 characters.
- `gender`: optional wording preference only; never used to infer astronomical values.
- `birth_date`: authoritative local Gregorian calendar date, accepted from `1600-01-01` through the current date and transported as `YYYY-MM-DD`.
- `birth_time`: authoritative local civil time with optional seconds; `NULL` when unknown.
- `birth_time_unknown`: explicitly identifies an unknown time. No noon or midnight substitute is invented.
- `location_id`: required foreign key to a verified stored location.
- `notes`: optional text, maximum 5,000 characters.
- `birth_time_utc`, `utc_offset_minutes`, `timezone_resolution_status`, and `timezone_fold`: calculation-preparation metadata derived without overwriting the local inputs.

Dates earlier than 1600 are outside this application's documented range. Python uses the proleptic Gregorian calendar. IANA data before 1970 can contain implementation- and zone-specific historical limitations; the application uses the installed `tzdata` interpretation and does not claim certainty beyond it.

## Location fields and validation

Locations store city, optional state/province, country, optional two-letter ISO country code, latitude (`-90` through `90`), longitude (`-180` through `180`), IANA timezone, and creation timestamp. Coordinate precision is `DECIMAL(10,7)`. Timezone abbreviations such as IST, CST, and PST are not accepted as substitutes for identifiers such as `Asia/Kolkata`.

Search checks stored city, state, and country text. Duplicate city names remain separate and the interface displays state, country, timezone, and coordinates. No result is selected automatically. Missing cities can be created only by entering verified coordinates and timezone; no geocoding provider or key is used.

Referenced locations may update descriptive labels, but their coordinates or timezone cannot be changed while birth profiles reference them. This prevents silently changing calculation inputs.

## Historical timezone handling

`backend/app/services/birth_time.py` combines the authoritative local date/time with the location's IANA timezone and round-trips candidate `fold` values through UTC.

- Normal time: returns/stores UTC and offset with status `resolved`.
- Clock rollback ambiguity: returns `ambiguous` and both candidate offsets until the user chooses fold `0` or `1`; the chosen result is stored as `resolved_ambiguous`.
- Clock advancement gap: returns HTTP 422 because the local civil time did not exist.
- Unknown birth time: stores no UTC guess and status `unknown_time`.
- Pre-migration records retain their original data and status `pending` until edited/revalidated.

UTC values are stored as timezone-naive MySQL `DATETIME` values by convention while the field name and API documentation identify them as UTC. The local date and time remain the authoritative source.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/locations` | Search/filter/page locations using `search`, `country`, `state`, `offset`, and `limit`. |
| POST | `/api/locations` | Create a validated verified location. |
| GET | `/api/locations/{id}` | Retrieve a location. |
| PATCH | `/api/locations/{id}` | Partially update a location with reference protection. |
| GET | `/api/birth-profiles` | Search/page profiles using `search`, `offset`, and `limit`. |
| POST | `/api/birth-profiles` | Create and timezone-resolve a profile. |
| GET | `/api/birth-profiles/{id}` | Retrieve a profile with its location. |
| PATCH | `/api/birth-profiles/{id}` | Safely update only supplied values and recompute UTC metadata. |
| POST | `/api/birth-time/validate` | Validate local civil time and return UTC preparation metadata. |

List endpoints return `X-Total-Count` while keeping list response bodies backward-compatible. Permanent deletion is intentionally absent.

## Database migration

Migration `20261112_02` reuses `users`, `locations`, and `birth_profiles`. It adds nullable `gender`, `birth_time_utc`, `utc_offset_minutes`, and `timezone_fold`, plus non-null `timezone_resolution_status` defaulting to `pending`. Check constraints limit fold to 0/1 and offset to ±1,440 minutes. No table or record is dropped.

## User interface

- `/kundli`: create a profile or enter a controlled verified location.
- `/birth-profiles/{id}/edit`: edit an existing profile.
- `/saved-charts`: clearly labeled Saved Birth Profiles with name search and pagination.
- `/birth-profiles/{id}`: show local inputs, location, coordinates, timezone, resolved UTC, and warnings.

The autocomplete debounces requests, cancels stale searches, reports loading/empty/error states, supports arrow-key/Enter selection, and never silently chooses an ambiguous city.

## Testing

```powershell
cd C:\wamp64\www\Projects\vedic-astrology\backend
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m alembic current

cd ..\frontend
npm.cmd run test
npm.cmd run typecheck
npm.cmd run build
```

Backend integration tests use `vedic_astrology_test` and clear only test-database rows. They cover CRUD, pagination/search, constraints, Unicode, reference failures, Kolkata/Berlin/Toronto offsets, rollback ambiguity, spring-forward gaps, and migration columns. Frontend tests mock APIs and cover required fields, unknown time, ambiguous cities, selection, create/update, ambiguity, loading, failures, search, pagination, themes, and mobile navigation.

## Manual verification

1. Start FastAPI on `127.0.0.1:8000` and Vite on `127.0.0.1:5173`.
2. Create a synthetic record: Test Person, `2000-01-15`, `10:30:00`, Chandigarh, `Asia/Kolkata`.
3. Confirm local time remains `10:30:00`, UTC is `05:00:00`, and offset is `330` minutes.
4. Open Saved Birth Profiles, view details, edit a non-critical field, and confirm location linkage remains unchanged.
5. Verify the row directly in MySQL or through a separate SQLAlchemy session after the API transaction completes.

## Privacy and production requirements

The APIs have no authentication. FastAPI must remain bound to loopback, CORS remains limited to local Vite origins, logs do not intentionally include complete payloads, and test data is synthetic. A nullable `user_id` is not ownership control. Before deployment, add authentication, per-record authorization, CSRF/threat review, audit policy, retention/deletion rules, encrypted transport, and production-specific secrets/database configuration.

The Vite base remains `/vedic-astrology/`; local and production databases must remain separate. No WAMPServer-specific logic appears in application services, and `tzdata` provides portable timezone data on Windows and production Python environments.

## Future calculation interface

The stored model now provides local date, exact local time, resolved UTC when possible, UTC offset, fold/status, latitude, longitude, and IANA timezone. Step 6 may consume these values through a dedicated astronomical service, but it must continue treating ambiguous, pending, and unknown-time profiles explicitly.
