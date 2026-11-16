# Report Test Results

Synthetic samples were generated on 2026-11-15 using Python 3.11.9, WeasyPrint 70.0, Pango 1.56.4, Swiss Ephemeris 2.10.03, Lahiri ayanamsa, mean node, and whole-sign houses.

| Sample | Pages | Size | Result |
|---|---:|---:|---|
| English summary | 5 | 34,579 bytes | A4, visually accepted |
| Hindi comprehensive | 8 | 75,818 bytes | A4, Devanagari shaping visually accepted |
| Punjabi comprehensive | 8 | 72,384 bytes | A4, Gurmukhi shaping visually accepted |

All 21 pages were rendered with Poppler and inspected. No missing-glyph boxes, clipping, chart misalignment, table overflow, or page-number defects were observed. Fonts are embedded, subset, and Unicode-mapped. Complex-script text is selectable, although Poppler extraction may insert spaces inside shaped Devanagari/Gurmukhi clusters, so exact copied-text search is renderer-dependent. Chart SVGs consume the same backend house and planet assignments shown in the React application.
