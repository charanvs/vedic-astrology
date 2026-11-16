# Navamsha (D9)

Each 30° Rashi is divided into nine equal parts of 3°20′. Parts are numbered 1–9 using half-open intervals.

The Parashari starting sign is:

- movable Rashi: the source Rashi itself;
- fixed Rashi: the ninth Rashi from the source;
- dual Rashi: the fifth Rashi from the source.

Counting proceeds forward from that start. The implementation also verifies the equivalent continuous rule: across all 108 segments from 0° Aries, the D9 Rashi is the segment index modulo 12. The degree within D9 is the fraction within the source segment scaled to 30°.

Examples: 19° Libra is the sixth Navamsha and maps to Pisces; 5° Taurus is the second Navamsha and maps to Aquarius. A graha is flagged `vargottama` only when its D1 and D9 Rashi numbers match.

See `DIVISIONAL_REFERENCE_TESTS.md` for source links and verification scope.
