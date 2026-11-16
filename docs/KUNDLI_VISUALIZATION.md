# North Indian Kundli visualization

## Scope

The `/kundli` workspace renders a North Indian diamond chart from the saved-profile calculation API. The browser does not perform astronomy: longitude, Rashi, Nakshatra, motion, Lagna, and whole-sign house assignments all come from the Step 6 backend.

## Fixed-house geometry

The SVG uses a square `600 × 600` view box. Houses stay fixed while Rashi numbers change according to the Lagna. House progression is anticlockwise.

| House | Fixed position |
| --- | --- |
| 1 | Top central diamond |
| 2 | Upper-left triangle |
| 3 | Left upper triangle |
| 4 | Left central diamond |
| 5 | Left lower triangle |
| 6 | Lower-left triangle |
| 7 | Bottom central diamond |
| 8 | Lower-right triangle |
| 9 | Right lower triangle |
| 10 | Right central diamond |
| 11 | Right upper triangle |
| 12 | Upper-right triangle |

This establishes the four cardinal houses as H1 top, H4 left, H7 bottom, and H10 right. The mapping follows the conventional fixed-house North Indian layout described by [AstroWord](https://www.astroword.in/learn/u1-l6) and the house-order explanation from [Apna Panchang](https://apnapanchang.in/en/guides/kundli-kaise-dekhe-12-bhav).

## Data contract

`GET /api/astrology/birth-profiles/{id}/calculate` returns a `houses` array with exactly twelve entries. Each entry contains the house number, assigned Rashi, planet identifiers, and Lagna marker. The frontend validates that:

- houses 1–12 occur exactly once;
- Rashis advance sequentially from the Lagna Rashi with wraparound;
- every supported graha occurs at most once in the calculation and exactly once in the chart;
- each graha's house and Rashi match its house entry.

An inconsistent response is rejected instead of being rendered misleadingly.

## Interaction and accessibility

- Houses and grahas support pointer, Enter, and Space activation.
- Selecting a graha also selects its house; selecting the corresponding table row produces the same state.
- Standard mode emphasizes compact chart labels. Detailed mode adds Rashi names and `(R)`/`(S)` motion markers.
- Every SVG house and graha has an accessible name and native SVG title. Focus is visibly indicated.
- The chart scales from small screens to a maximum desktop width without changing its square aspect ratio.
- SVG export serializes the rendered chart with resolved colors and excludes the person's name from the filename.

Unknown birth time profiles cannot generate Lagna or houses and therefore show an explicit blocking message.

## Display, layout, and export

Standard mode shows Rashi numbers, compact graha abbreviations, and the Lagna marker. Detailed mode adds sign names and motion indicators. The companion panels retain full details when the compact labels are necessary on a 375 px screen. Responsive CSS stacks the chart and detail panel below the desktop breakpoint; the SVG remains square at mobile, tablet, laptop, and desktop widths. Existing CSS variables provide light, dark, focus, selection, and print colors.

Export serializes the actual displayed SVG, resolves its theme colors, and adds only the numeric profile reference as metadata. The filename is `kundli-profile-{id}.svg`; user-entered names are not inserted into SVG markup or filenames. PNG and PDF export are intentionally deferred to avoid new rendering dependencies.

## Data flow and testing

The flow is MySQL birth profile → FastAPI saved-profile calculation → typed calculation response → strict `transformKundliData` validation → reusable SVG and tabular view. Synthetic Mesha, Tula, and Makara fixtures test Rashi rotation independently of astronomical accuracy. Backend tests cover real Swiss Ephemeris calculations, node opposition, whole-sign assignments, schema validity, and unknown-time rejection. Component tests cover geometry, rendering, display modes, pointer and keyboard selection, error states, synchronized panels, and SVG export.

## Known limitations

- Step 7 uses whole-sign houses and the mean lunar node convention selected in Step 6.
- It does not calculate aspects, combustion, dignity, predictions, Panchang, Dasha, or matching.
- Very dense houses use compact abbreviations; the synchronized table is the authoritative accessible detail view.
- No external astrology chart was used to independently validate a person's real-world chart in this milestone; validation covers internal API consistency and established engine reference tests.
- Public profile access remains blocked until authentication, ownership enforcement, and production privacy controls exist.

A later reporting milestone may consume the standalone SVG when implementing PDF reports. Step 7 does not add PDF generation.
