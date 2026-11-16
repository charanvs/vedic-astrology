# Ashtakoota Kundli Matching

## Scope

Step 10 implements the traditional North Indian eight-part Guna Milan score. It compares the two sidereal Moons and returns Varna 1, Vashya 2, Tara 3, Yoni 4, Graha Maitri 5, Gana 6, Bhakoot 7, and Nadi 8: exactly 36 maximum points. Scores use `Decimal`; there are no bonuses, hidden penalties, or score-changing exceptions.

The module is educational. Compatibility scores represent traditional astrological beliefs and are not scientifically validated predictions of relationship success. It does not recommend marriage, rejection, separation, or any medical or fertility conclusion.

## Inputs and Moon calculation

Saved profiles reuse the Step 6 Swiss Ephemeris geocentric Moon with sidereal zodiac and Lahiri (Chitrapaksha) ayanamsa. Exact birth times use their stored UTC instant and historical IANA timezone resolution. Names and stored gender never determine the score.

For an unknown birth time, the resolver evaluates the complete local civil date at half-hour intervals plus both interval limits. It returns a definitive result only if Moon Rashi and Nakshatra remain unchanged throughout. The response labels this `date_unambiguous`. A relevant boundary crossing produces HTTP 422 with the possible placements; the system never assumes noon.

## Roles and ruleset

Both partners receive an explicit `bride` or `groom` calculation-table role. The two roles must differ. The ruleset reads directional matrices as bride row and groom column. Changing roles can change Varna, Gana, Yoni, Graha Maitri, or Vashya values; it never changes astronomical Moon data.

The only supported ruleset is `muhurta_chintamani_joshi_v1`. See `MATCHING_RULESETS.md` for every mapping and matrix.

## Result and observations

The backend calculates all eight rows, validates each range, and sums them exactly. The commonly cited 18/36 value is presented only as a configurable traditional threshold. Nadi, Bhakoot, and low Gana conditions are returned as separate observations. No cancellation rule changes the base score in this release.

## API

- `POST /api/matching/calculate`: calculate from two validated sidereal Moon longitudes and explicit roles.
- `POST /api/matching/birth-profiles`: calculate from two different saved profiles; local-development-only.
- `GET /api/matching/config`: supported rulesets, maxima, engine, and ayanamsa.
- `GET /api/matching/rules`: public non-sensitive mappings, matrices, conventions, and bibliographic metadata.

The response minimizes personal data to profile ID, name, role, and derived Moon classifications. Results are calculated on demand and are not persisted.

## React interface

`/matching` provides two independently searchable profile selectors, explicit role controls, stored birth details, a submit action, loading/error handling, score progress bar with text alternative, eight-row accessible table, expandable explanations, separate observations, and Moon comparison details. It uses backend values only and supports existing light/dark themes and narrow-screen horizontal table scrolling.

English strings are centralized in `matchingText.ts`; the structure is ready for verified Hindi and Punjabi translations, but those languages are not claimed as complete.

## Security and deployment

Saved-profile matching is blocked outside the development environment until authentication, ownership authorization, consent, auditing, and retention policies exist. CORS remains environment-limited. No comparison history or public link is created.

Future GoDaddy deployment must retain environment-driven database/API configuration, separate production/local MySQL, Linux timezone data, `/vedic-astrology/` asset/router bases, and Swiss Ephemeris license compliance. Nothing was deployed in Step 10.

## Excluded work

Manglik Dosha, Navamsha matching, South Indian Dasa Porutham, Muhurat, predictions, PDF reports, and Step 11 divisional charts are not implemented.
