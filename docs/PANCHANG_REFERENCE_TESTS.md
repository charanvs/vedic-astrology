# Panchang independent reference validation

Validation was performed on 2026-11-13 against independent public Panchang pages. Application values below were generated locally with Swiss Ephemeris 2.10.03, `pyswisseph` 2.10.3.2, the Moshier source, Lahiri sidereal mode, the listed coordinates, and the apparent upper solar limb/refraction convention. Times are local and rounded to the nearest displayed minute for comparison.

The acceptance tolerance is two minutes for lunar element boundaries and three minutes for solar events. These tolerances accommodate publisher rounding and undocumented differences in coordinates, elevation, ephemeris data, ayanamsa realization, and refraction. Identity of the active element must match exactly.

| Reference | Location and input | Date | Element | Reference | Application | Difference | Result |
|---|---|---:|---|---:|---:|---:|---|
| Drik Panchang | Chandigarh, 30.7333 N, 76.7794 E, Asia/Kolkata | 2026-11-13 | Sunrise | 06:47 | 06:47:19 | 19 sec | Pass |
| Drik Panchang | Chandigarh | 2026-11-13 | Shukla Chaturthi ends | 20:42 | 20:43:05 | 1 min 5 sec | Pass |
| Drik Panchang | Chandigarh | 2026-11-13 | Mula ends | 17:17 | 17:17:27 | 27 sec | Pass |
| MyPanchang | Chandigarh | 2026-11-13 | Dhriti ends | 05:22:08 next day | 05:23:00 next day | 52 sec | Pass |
| MyPanchang | Chandigarh | 2026-11-13 | Vanija ends | 07:24:25 | 07:24:47 | 22 sec | Pass |
| Drik Panchang | New Delhi, 28.6139 N, 77.2090 E, Asia/Kolkata | 2026-11-13 | Sunrise | 06:42 | 06:42:00 | < 1 min | Pass |
| Drik Panchang | New Delhi | 2026-11-13 | Shukla Chaturthi ends | 20:42 | 20:43:04 | 1 min 4 sec | Pass |
| Drik Panchang | New Delhi | 2026-11-13 | Mula ends | 17:17 | 17:17:27 | 27 sec | Pass |
| Dev Panchang | Mumbai, 19.0760 N, 72.8777 E, Asia/Kolkata | 2026-06-21 | Sunrise | 06:01 | 06:01:53 | 53 sec | Pass |
| AstroAmrit | Mumbai | 2026-06-21 | Shukla Saptami ends | 15:21 | 15:21:08 | 8 sec | Pass |
| AstroAmrit | Mumbai | 2026-06-21 | Purva Phalguni ends | 09:31 | 09:31:34 | 34 sec | Pass |
| AstroAmrit | Mumbai | 2026-06-21 | Siddhi ends | 11:21 | 11:21:31 | 31 sec | Pass |
| Dev Panchang | Chennai, 13.0827 N, 80.2707 E, Asia/Kolkata | 2026-03-20 | Sunrise | 06:13 | 06:13:19 | 19 sec | Pass |
| Dhyayan Astro | Chennai | 2026-03-20 | Shukla Dwitiya ends | 02:31 next day | 02:31:22 next day | 22 sec | Pass |
| Dhyayan Astro | Chennai | 2026-03-20 | Revati ends | 02:27 next day | 02:27:57 next day | 57 sec | Pass |
| Pauranik | Chennai | 2026-03-20 | Brahma ends | 22:16 | 22:15:00 | 1 min | Pass |
| VedicSpace | New York, 40.7128 N, 74.0060 W, America/New_York | 2026-09-22 | Sunrise | 06:43 | 06:43:40 | 40 sec | Pass |
| VedicSpace | New York | 2026-09-22 | Shukla Ekadashi ends | 12:13 | 12:13:49 | 49 sec | Pass |
| VedicSpace | New York | 2026-09-22 | Shravana ends | 23:39 | 23:39:22 | 22 sec | Pass |
| VedicSpace | New York | 2026-09-22 | Atiganda ends | 06:59 | 06:59:25 | 25 sec | Pass |

The five requested geographic comparisons were attempted and obtained: Chandigarh, New Delhi, Mumbai, Chennai, and an international location (New York). Chandigarh was cross-checked with two publishers. Mumbai and Chennai search results also exposed multiple mutually agreeing publishers. All active Tithi, Nakshatra, Yoga, Karana, Paksha, and Vara identities matched for the recorded cases.

## Interpretation

The largest recorded lunar-boundary difference is 1 minute 5 seconds, within the declared two-minute tolerance. Solar times are also within tolerance. This supports the implementation but is not a proof that publishers use identical conventions. In particular, most reference pages do not expose exact elevation, pressure/temperature, source ephemeris version, or a numerical ayanamsa value for the instant.

No application value was copied into the engine or stored as a production lookup. The Chandigarh assertions in the automated suite are regression checks; the other city outputs were generated independently by the same generic service with different dates, coordinates, and timezones.

## Reference pages

- [Drik Panchang — Chandigarh, 13 November 2026](https://www.drikpanchang.com/panchang/day-panchang.html?geoname-id=1274746)
- [Drik Panchang — New Delhi, 13 November 2026](https://www.drikpanchang.com/panchang/day-panchang.html?l=20413&time-format=24plushour)
- [MyPanchang — Chandigarh, 13 November 2026](https://www.mypanchang.com/en/panchang/2026/11/13/loc/1274746)
- [AstroAmrit — Mumbai, 21 June 2026](https://astroamrit.com/panchang/mumbai/2026-06-21)
- [Dev Panchang — Mumbai, 21 June 2026](https://devpanchang.in/en/panchang/mumbai/2026-06-21)
- [Dhyayan Astro — Chennai, 20 March 2026](https://astro.dhyayan.com/panchang/chennai/2026-03-20)
- [Pauranik — Chennai, 20 March 2026](https://pauranik.org/en/panchang/chennai-in/2026/03/20)
- [VedicSpace — New York, 22 September 2026](https://vedicspace.com/panchang/new-york/2026-09-22/)
- [Swiss Ephemeris programmer documentation](https://www.astro.com/swisseph/swephprg.2.10.pdf)

## Automated coverage

`backend/tests/test_panchang_step8.py` covers all 30 Tithis, all 27 Yogas, every one of the 60 Karana positions, the fixed-Karana placements, angular wraparound, all seven Varas and the sunrise boundary, Indian/European/North American solar events, high-latitude missing sunrise, schema validation, API validation, invalid location, unavailable ephemeris, and the Chandigarh reference case. Existing Step 6 and Step 7 tests are included in the full backend regression command.
