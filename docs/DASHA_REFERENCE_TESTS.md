# Dasha Reference Tests

## Method

Automated tests combine independent hand-worked proportions with a published New Delhi timeline. Comparisons use the source's stated convention where possible. A date-only agreement does not imply identical sub-second timestamps: sources often omit time, use rounded Moon coordinates, or use 365.2425 instead of this application's default 365.25-day year.

## Results

| Reference | Expected | Application result | Difference | Result |
|---|---|---|---|---|
| Witchcraft Daily, Moon halfway through Ashwini | Ketu balance 3.5 years | 3.5 years | 0 | Pass |
| Witchcraft Daily, Ketu/Ketu proportion | `7 * 7 / 120 = 0.408333...` years | Same Decimal proportion | 0 before timestamp rounding | Pass |
| Sanatan Veda, Moon at Gemini 23°56′ in Punarvasu | Jupiter balance 11.28 years | 11.28 years | 0 | Pass |
| Mathematical Astrology, Rohini with 193/800 remaining | Moon balance 2.4125 nominal years | 2.4125 years | 0 | Pass |
| AstroScorpio, 19 Jan 2001 14:05 New Delhi | Anuradha/Saturn; Saturn start 27 May 1993; Mercury 27 May 2012–27 May 2029 | Same Nakshatra/lord and local calendar dates | 0 calendar days | Pass |
| Same published case at 13 Nov 2026 | Mercury/Saturn/Saturn; Pratyantardasha ends 19 Feb 2027 | Same hierarchy and local end date | 0 calendar days | Pass |

The published New Delhi source states a 365.2425-day convention, while this application test deliberately uses its documented 365.25-day default. Its displayed dates are day precision, and all compared dates agree. The application's exact times should not be presented as identical to a source that does not publish them.

## Sources

- [AstroScorpio Dasha calculator and worked New Delhi example](https://astroscorpio.com/dasha-calculator)
- [Witchcraft Daily Vimshottari formulas and halfway-Ashwini example](https://witchcraftdaily.com/vedic/library/vimshottari-dasha/index.html)
- [Sanatan Veda worked Punarvasu balance](https://www.sanatanveda.com/astrology/calculation-of-vimshottari-dasha-system/)
- [Mathematical Astrology worked Rohini balance (PDF)](https://storage.yandexcloud.net/j108/library/zjhjjzy2/Y.K._Bansal_-_Mathematical_Astrology.pdf)

## Coverage

`backend/tests/test_dasha_step9.py` verifies all nine starting lords, sequence wraparound, Nakshatra start/midpoint/end/boundary behavior, 120-year coverage, exact child partitioning, current-period transitions, both year conventions, historical timezone rendering, out-of-range errors, schemas, and APIs. Frontend tests cover loading, errors, profile selection, birth/current panels, convention and reference changes, proportional timeline selection, and hierarchy navigation.

Known comparison limits: independent sources do not all disclose raw ephemeris longitude, timestamp rounding, timezone database version, or full UTC timestamps. No claim is made beyond the documented quantities above.
