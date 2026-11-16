# Divisional Reference Tests

## Sources

- Bṛhat Parāśara Horā Śāstra, chapter 6, verses 12–13: <https://indike.org/pramana/in.astro.hora.yavana.brhatparasara.6>
- D9 calculation and worked examples: <https://jyotishya.date/learn/navamsa-d9/>
- D10 full table and worked examples: <https://www.astroword.in/learn/u6-l7>

The primary text states the movable/fixed/dual D9 starts and odd/even D10 starts. Secondary worked examples are used as transparent cross-checks, not as an ephemeris source.

## Automated coverage

- Every one of the 108 D9 segments is checked against the continuous-count identity.
- Every one of the 120 D10 sign/segment combinations is checked against the odd/even starting-sign rule.
- Published examples are asserted for Libra, Taurus, Aries, and Virgo.
- Exact boundaries, just-before-boundary values, 360° normalization, non-finite rejection, house rebuilding, and D9 Vargottama are tested.
- The configuration and calculation API contracts are tested with the native Swiss Ephemeris-backed Step 6 calculation.

Decimal arithmetic is used inside the pure transformation functions. Incoming binary floats are converted through their decimal string representation; the original Step 6 precision is not rounded for display before transformation.
