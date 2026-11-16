# Daily Panchang calculations

## Convention and scope

The Step 8 module implements an on-demand Drik Ganita daily Panchang. It uses the existing Step 6 Swiss Ephemeris facade, Lahiri (Chitrapaksha) sidereal mode, geocentric Sun and Moon ecliptic longitudes, and the selected location's IANA timezone. The five elements are evaluated at local sunrise. The traditional day extends from that sunrise to the next local sunrise; it is distinct from the civil date, which changes at midnight.

This module provides astronomical calendar values and short educational definitions. It does not provide personal predictions, festivals, lunar-month naming, Muhurta recommendations, Rahu Kalam, Choghadiya, or Dasha calculations.

## Engine and solar events

The validated development environment uses Swiss Ephemeris 2.10.03 through `pyswisseph` 2.10.3.2 on Python 3.11.9. `ASTROLOGY_EPHEMERIS_SOURCE=moshier` selects the file-free Moshier analytical ephemeris; setting `swiss` requires an explicitly configured directory containing official `.se1` files. Source flags are checked so a requested source cannot silently fall back.

Sunrise and sunset use `swisseph.rise_trans` with the Sun, the configured ephemeris flag, geographic longitude/latitude, optional elevation, apparent upper-limb convention, and atmospheric refraction. Pressure is passed as zero so Swiss Ephemeris estimates it from elevation; temperature is 15°C. A search begins before local civil midnight, converts candidates to the selected IANA zone, and accepts only an event whose local date equals the requested date. This handles UTC-date crossings and daylight-saving changes.

If sunrise or the following sunrise does not occur, the API returns an explicit 422 response because a sunrise-anchored day cannot be constructed. A missing sunset is represented as unavailable in an otherwise bounded result. No replacement time is invented.

## Five elements

All angles are normalized to `0 <= angle < 360`.

- **Tithi:** `E = normalize(Moon - Sun)` and `floor(E / 12) + 1`. Values 1–15 are Shukla Paksha and 16–30 are Krishna Paksha. Number 15 is Purnima and 30 is Amavasya.
- **Vara:** the weekday of the local sunrise. For an arbitrary instant before that date's sunrise, the preceding sunrise-based Vara remains active.
- **Nakshatra:** reused from the Step 6 implementation: `floor(Moon / (360 / 27)) + 1`, using the Lahiri sidereal Moon. The Pada is `floor(position within Nakshatra / (10 / 3)) + 1`.
- **Yoga:** `Y = normalize(Sun + Moon)` and `floor(Y / (360 / 27)) + 1`, using Lahiri sidereal longitudes.
- **Karana:** each six-degree elongation interval is one half-Tithi. Position 1 is Kimstughna; the seven movable Karanas repeat through positions 2–57; positions 58–60 are Shakuni, Chatushpada, and Naga.

## Transition solver

One reusable solver searches Tithi, Nakshatra, Yoga, and Karana boundaries. It samples a bounded interval in two-hour steps, unwraps each increasing angular function locally across 360/0, brackets every boundary, and bisects to a time interval of at most 0.25 seconds. It recalculates the element one second before and after each root when creating transition labels. A discontinuity above 90 degrees, invalid interval, or failure to converge raises a typed calculation error rather than returning an estimate.

For the element active at sunrise, the service searches back three days to obtain its start and forward through the next sunrise to obtain its end. Every transition inside the Panchang day is included and sorted with sunrise, sunset, and next sunrise. Timestamps contain both timezone-aware UTC and local ISO 8601 values.

## API

- `GET /api/panchang/daily?date=YYYY-MM-DD&location_id=N` uses an existing stored location.
- `POST /api/panchang/calculate` accepts a date, validated latitude/longitude, IANA timezone, display location fields, and optional elevation.
- `GET /api/panchang/config` reports the convention, engine metadata, date range, timezone handling, and day definition without server paths or credentials.

Dates are limited to years 1600–2399. Coordinates and IANA zones are validated. Ephemeris unavailability returns 503; unsupported astronomical conditions and solver failures return 422; an unknown stored location returns 404. Results are not automatically persisted, and Step 8 adds no database migration.

## Frontend

The `/panchang` route contains a stored-location search/select control, location-relative date picker, previous/next/Today navigation, five keyboard-operable element cards, solar panel, detail panel, and chronological transition timeline. API failures never substitute mock values. The component layout is responsive from mobile through wide desktop and uses the existing light/dark/system theme tokens.

Primary components are in `frontend/src/components/panchang/`; API contracts are in `frontend/src/types/api.ts` and requests use the shared Axios client.

## Performance and portability

Each request creates one bounded service instance and caches Sun/Moon longitudes by body and UTC instant for that calculation. Transition searches cannot loop beyond their date bounds. No worker, cache service, PHP dependency, Windows path, or new database table was added. The Vite base and Router basename remain compatible with `/vedic-astrology/`.

Public deployment remains blocked pending authentication/authorization for private profiles, rate limiting for calculation endpoints, GoDaddy Python/ASGI verification, production environment configuration, separate production MySQL credentials, and resolution of Swiss Ephemeris licensing obligations.

## Known limitations

- Moshier is the configured local source; optional Swiss `.se1` files can provide a different precision/range profile.
- Refraction, elevation, coordinates, ayanamsa implementation, and rounding conventions can produce small differences between publishers.
- The UI is English-first. Its centralized strings and flexible layout prepare for Hindi and Punjabi, but full translations are not claimed.
- Extremely high latitudes can lack sunrise or sunset on a civil date.
- Reference sites do not always publish exact coordinates, elevation, ephemeris version, ayanamsa implementation, or solar-disc/refraction conventions.

