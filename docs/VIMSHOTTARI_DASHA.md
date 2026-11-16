# Vimshottari Dasha

## Calculation contract

The module implements the traditional 120-Dasha-year sequence:

| Order | Lord | Years |
|---:|---|---:|
| 1 | Ketu | 7 |
| 2 | Venus | 20 |
| 3 | Sun | 6 |
| 4 | Moon | 10 |
| 5 | Mars | 7 |
| 6 | Rahu | 18 |
| 7 | Jupiter | 16 |
| 8 | Saturn | 19 |
| 9 | Mercury | 17 |

The sequence and durations are centralized and immutable. They are traditional proportional divisions, not physical orbital periods.

## Birth Moon and balance

The service reuses the Step 6 Swiss Ephemeris calculation: geocentric sidereal Moon longitude with Lahiri (Chitrapaksha) ayanamsa. It uses the full calculation value, not the formatted longitude. The 27 equal Nakshatras are indexed by `longitude * 27 / 360`; their lords repeat in the Dasha sequence.

For the birth Nakshatra:

```text
elapsed fraction   = fractional part of (Moon longitude * 27 / 360)
remaining fraction = 1 - elapsed fraction
elapsed years      = lord years * elapsed fraction
remaining years    = lord years * remaining fraction
theoretical start  = birth UTC - elapsed years * selected days/year * 86,400 seconds
```

The first Mahadasha therefore usually begins before birth. Its full theoretical subperiods are retained; they are never restarted or compressed at birth.

## Period hierarchy and arithmetic

Nine Mahadashas form one 120-year cycle starting with the birth Nakshatra lord. A parent period is divided into nine children beginning with the parent lord:

```text
child proportion = child lord years / 120
```

The same rule creates Antardashas and Pratyantardashas. All calculations use `Decimal`, UTC, exact 86,400-second days, and integer microseconds with half-even rounding only at timestamp conversion. Child boundaries are calculated from the authoritative parent start/end; the ninth child is explicitly assigned the parent end. Intervals are `[start, end)`, so an exact transition belongs to the new period.

The default convention is exactly 365.25 days per Dasha year. The optional Savana convention is exactly 360 days. Switching convention recalculates every timestamp; conventions are never mixed. A difference from software using civil-year addition, 365.2425 days, or a 360-day calendar breakdown is expected and is recorded in the response.

UTC is authoritative. Birth and period timestamps are also rendered with the profile's IANA timezone, including its historical offset. The selected reference instant must be timezone-aware and fall in the generated cycle.

## API

- `POST /api/dasha/calculate` validates explicit birth data, convention, reference instant, and detail level.
- `GET /api/dasha/birth-profiles/{id}` calculates the full saved-profile timeline.
- `GET /api/dasha/birth-profiles/{id}/current` returns the active three-level hierarchy.
- `GET /api/dasha/config` reports conventions, sequence, durations, detail levels, engine, and ayanamsa.

Saved-profile endpoints are limited to the local development environment until authentication, ownership authorization, and privacy controls exist. Profiles with unknown birth times are rejected because a precise Dasha timeline cannot be calculated honestly.

## React interface

`/dasha` provides a saved-profile selector, 365.25/360-day selector, optional UTC reference datetime, birth-balance summary, current three-level hierarchy, a proportional nine-Mahadasha timeline, and a selected Mahadasha/Antardasha hierarchy. Timeline buttons are keyboard accessible and horizontally scroll on narrow screens. Dates use the API's profile-local timestamps rather than browser-local reinterpretation.

The UI explains the traditional model without offering life-event predictions or claiming scientific validation.

## Limitations and production considerations

- Only Mahadasha, Antardasha, and Pratyantardasha are implemented; Sookshma and Prana are out of scope.
- Periods are calculated on demand and are not cached in MySQL.
- Dates can differ from other products when year-length, ayanamsa, ephemeris, node, timezone, or rounding conventions differ.
- Public deployment remains blocked until profile authentication/authorization and Swiss Ephemeris licensing are resolved.
- Production must keep environment-driven database/API configuration, the `/vedic-astrology/` Vite base and router basename, Linux timezone data, and separate local/production databases.

See `DASHA_REFERENCE_TESTS.md` for independent comparisons.
