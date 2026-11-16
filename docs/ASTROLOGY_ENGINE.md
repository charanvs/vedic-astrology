# Astrology Calculation Engine

## Status

Step 6 implements the calculation architecture and UI without changing the database schema. The validated Windows runtime uses Python 3.11 and the established `pyswisseph` wheel.

## Binding and runtime

The selected package is `pyswisseph==2.10.3.2`, exposing `import swisseph as swe` and Swiss Ephemeris 2.10.03. It was selected because its established CPython 3.11 Windows wheel imports successfully under this machine's Application Control policy. Python 3.14 has no compatible wheel, and building from source requires Microsoft Visual C++ 14+.

Recommended local runtime:

```powershell
py -3.11 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

The native binding, Lahiri ayanamsa, Moshier planetary calculation, and `houses_ex` ascendant calculation were verified after installation.

## Configuration

| Variable | Values | Meaning |
| --- | --- | --- |
| `ASTROLOGY_EPHEMERIS_SOURCE` | `moshier` or `swiss` | Explicit calculation backend; default is deliberate Moshier. |
| `ASTROLOGY_EPHE_PATH` | portable directory path | Required for `swiss`; must contain official `.se1` files. |
| `ASTROLOGY_STATIONARY_THRESHOLD` | positive degrees/day | Default `0.0001`. |

Moshier is file-free and explicitly requested with `FLG_MOSEPH`. Swiss-file mode requests `FLG_SWIEPH`, verifies the directory, and verifies the returned flag after every `calc_ut` call. Swiss Ephemeris documents that missing files can otherwise cause an automatic Moshier fallback; this implementation treats that as an error.

No Windows path is hardcoded. The API never returns the configured filesystem path.

## Fixed conventions

- Zodiac: sidereal.
- Ayanamsa: Lahiri/Chitrapaksha, `SIDM_LAHIRI`.
- Reference: geocentric, apparent ecliptic position.
- Nodes: mean lunar node for Rahu; Ketu is exactly opposite.
- Houses: actual sidereal ascendant from `houses_ex`; planet houses are whole-sign assignments from its Rashi.
- Calendar: proleptic Gregorian, years 1600 through 2399.
- Time: authoritative Step 5 local civil time is converted to UTC; `calc_ut` receives Julian Day UT.

Ketu has no fabricated independent latitude or speed. Its motion is labeled `derived`. Longitudes remain full-precision until sign and Nakshatra assignment; formatted DMS is a separate field.

## Global state and concurrency

Swiss Ephemeris path and sidereal mode are process-global. `Ephemeris` owns a re-entrant lock and, inside that lock, reapplies `SIDM_LAHIRI`, source configuration, and the calculation. No unrelated module calls state-changing functions. Multiple worker processes have independent library state; threads in each process are serialized around it.

## Julian Day and timescales

The conversion handles seconds, microseconds, and UTC date rollover. The application distinguishes UTC input from UT1 and TT: it supplies JD UT to `calc_ut`, and Swiss Ephemeris applies its Delta-T model internally. Historical UTC/UT1, Delta-T, timezone, and calendar uncertainty limits apply, especially for early dates.

## API

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/api/astrology/config` | Non-sensitive conventions, supported bodies, configured source, and engine availability. |
| POST | `/api/astrology/calculate` | Validated local civil birth data and location calculation. |
| GET | `/api/astrology/birth-profiles/{id}/calculate` | On-demand saved-profile calculation; development environment only. |

Unknown birth time, unresolved ambiguity, missing profiles, invalid coordinates/timezones, unsupported years, engine failure, and source mismatch return explicit errors. Saved-profile calculation is blocked outside `APP_ENV=development` until authentication and ownership checks exist.

## Frontend

`/planets` loads saved profiles, requests actual API results, and shows Graha, sidereal longitude, Rashi, degree in Rashi, Nakshatra, Pada, whole-sign house, and motion. The Kundli/profile page requests a summary after a successful save. It shows Lagna, Moon Rashi/Nakshatra/Pada, Lahiri ayanamsa, and engine source. Unknown birth time displays a warning instead.

The North Indian diamond chart, Panchang, Dasha, matching, and interpretations remain outside Step 6.

## Deployment

GoDaddy must support a compatible CPython runtime and native extension, and the package must be tested on its Linux image. Official ephemeris files, if selected, must be deployed separately with an environment-driven path and checked for the required date segments. Public activation is blocked by both authentication/ownership work and the unresolved Swiss Ephemeris license decision.
