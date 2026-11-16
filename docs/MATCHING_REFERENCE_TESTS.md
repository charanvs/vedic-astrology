# Matching Reference Validation

## Results

| Reference | Ruleset | Expected eight scores | Actual eight scores | Expected | Actual | Difference | Result |
|---|---|---|---|---:|---:|---:|---|
| Telugu Calendar: bride Rohini P2 / groom Hasta P3 | Muhurta Chintamani Joshi | 1, 0.5, 3, 2, 5, 6, 0, 8 | Same | 25.5 | 25.5 | 0 | Pass |
| Bharat Ephemeris: bride Bharani / groom Ashwini | Published North Indian table compatible with selected cells | 1, 2, 3, 2, 5, 6, 7, 8 | Same | 34 | 34 | 0 | Pass |
| Himalaya Vedic World sample: bride Uttara Bhadrapada / groom Hasta | Published Ashtakoota report compatible with selected cells | 0, 0.5, 1.5, 3, 0.5, 6, 7, 8 | Same | 26.5 | 26.5 | 0 | Pass |
| Astrojar/Charak: bride Uttara Bhadrapada / groom Mula | Alternate Vashya convention | 0, 0.5, 1.5, 2, 5, 0, 7, 8 | 0, 2, 1.5, 2, 5, 0, 7, 8 | 24 | 25.5 | +1.5 | Expected convention difference |

The first reference publishes its [complete methodology and source pages](https://thetelugucalendar.com/marriage-matching/method/) and [Rohini–Hasta worked result](https://thetelugucalendar.com/marriage-matching/). The second publishes an [Ashwini–Bharani 34/36 breakdown](https://bharatephemeris.com/kundli-matching/ashwini/bharani). The third is an independently generated [sample report](https://himalayavedicworld.com/pdf/ekundali10Pdf/EK10MarriageMatchingEnglish.pdf). The fourth [Mula–Uttara Bhadrapada example](https://astrojar.in/blog/ashtakoot-matching/) uses a degree-split/Manava classification for Sagittarius, while the selected Muhurta Chintamani table classifies all Sagittarius as Chatushpada. The code is not altered to conceal that regional ruleset difference.

## Automated coverage

`test_matching_step10.py` runs all 729 ordered Nakshatra pairs and confirms deterministic, bounded rows and exact totals. It separately checks all 144 ordered Rashi pairs; all Vashya, Yoni, Gana, and classical-planet matrix cells; all Tara categories and wraparound; sign boundaries; role reversal; safe unknown-time behavior; Pydantic responses; and API validation.

Exhaustive internal coverage proves implementation consistency, not historical truth. Printed traditions differ particularly for Vashya and Yoni; results are reproducible only with the named versioned ruleset.
