# Astronomical Reference Cases

## Verified independent case

| Case | Source and convention | Expected | Actual | Difference | Tolerance | Result |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2000-01-01 12:00:00 UT | U.S. Naval Observatory Julian Date Converter, Gregorian/UT1 | JD 2451545.000000 | JD 2451545.000000 | 0 days | 1e-9 day | Pass |

Reference: [USNO Julian Date Converter](https://aa.usno.navy.mil/calculated/juliandate?ID=AA&date=2000-01-01&era=AD&submit=Get+Date&time=12%3A00%3A00.000).

The suite also verifies one-second and fractional-second increments, leap-day rollover, all 12 exact Rashi boundaries, values immediately below boundaries, all 27 Nakshatras, all four Padas, the Vimshottari lord cycle, longitude normalization, whole-sign assignments, and motion thresholds. These mathematical boundary tests are not substitutes for independent planetary validation.

## Live engine status and remaining independent comparisons

| Reference area | Intended comparison | Tolerance | Current status |
| --- | --- | --- | --- |
| Lahiri ayanamsa | Swiss Ephemeris `SIDM_LAHIRI` value at multiple dates | 1 arcsecond | Live calculation passes; independent published comparison pending. |
| Classical planets | Independently generated Swiss Ephemeris test-program longitudes | 1 arcsecond with identical flags/source | Live calculation passes; independent published comparison pending. |
| Mean Rahu | Independent mean-node longitude | 1 arcsecond | Live calculation passes; independent published comparison pending. |
| Lagna | Independent `houses_ex` sidereal ascendant for India, Europe, and North America | 0.01 degree | Live calculation passes; multi-location independent comparison pending. |
| Source flags | Returned `FLG_MOSEPH` or `FLG_SWIEPH` equals requested source | Exact bit match | Pass for configured Moshier source. |

No expected planetary, Ayanamsa, or Lagna value has been invented. Live calculations are operational, but independent astronomical comparison coverage remains provisional. The official programmer documentation defines returned-flag fallback behavior and sidereal `houses_ex`: [Swiss Ephemeris programming interface](https://www.astro.com/swisseph/swephprg.htm).

## Reproduction commands

```powershell
cd C:\\wamp64\\www\\Projects\\vedic-astrology\\backend
.\\.venv\\Scripts\\python.exe -m pytest

cd ..\\frontend
npm.cmd run test
npm.cmd run typecheck
npm.cmd run build
```
