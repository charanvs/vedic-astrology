# Changelog

## Unreleased - 2026-11-16 (production readiness)

- Licensed the application under the GNU AGPL v3 or later to use the Swiss Ephemeris Free Edition; footer links to the configured source repository and credits GeoNames (CC BY 4.0).
- Added a cPanel/GoDaddy deployment pack (`backend/deploy/build_release.py`): Passenger WSGI entry point via a2wsgi, single-app hosting of the React build at `/astrology`, offline `schema.sql`, production requirements for Python 3.11, server self-check and migration scripts, and `docs/DEPLOYMENT_GODADDY.md`.
- Production fixes: registration no longer fails without SMTP when email verification is off; the app starts even if PDF system libraries are missing (PDF endpoints then return 503); base path changed from `/vedic-astrology` to `/astrology`; both `cvstudy.in` and `www.cvstudy.in` accepted.
- Kundli Matching page: **Print full report** (with a report-language choice) under each result opens the complete matching report for the same profiles, roles and ruleset as a print-ready page.
- Printable report fallback: when the server's Pango is older than 1.44 (checked by version, since an old Pango imports but fails mid-render), the Reports page opens the same report as a print-ready page and the reader saves it with the browser's “Save as PDF”. New endpoints `POST /api/reports/{kundli,matching}/printable` and `GET /api/reports/fonts/{name}` (fixed list of bundled Noto fonts).
- Added administrator approval of self-registered accounts with an admin dashboard, account preferences, offline city search, and traditional interpretation, matching and period-wise forecast sections in PDF reports.

## 1.2.0 - 2026-11-15

- Added normalized email registration, Argon2id password hashing, verification, login/logout, recovery, password change, and safe local admin provisioning.
- Added opaque hashed server sessions with idle/absolute expiry, revocation, secure cookie profiles, session listing, and synchronizer-token CSRF protection.
- Enforced authenticated ownership across birth profiles, saved D1, Dasha, D9/D10, matching, and PDF generation; quarantined four legacy unowned profiles.
- Added MySQL-backed rate limits, audit events, restricted CORS/trusted hosts, security headers, consistent request IDs, and strict mass-assignment validation.
- Added account UI, protected React routes, session authority through `/api/auth/me`, data export, and a reauthenticated deletion-request workflow.
- Added additive Alembic revision `20261115_01`, pre-migration backup verification, authentication/authorization tests, and production/GoDaddy security documentation.
- Public release remains blocked on live SMTP, legacy profile ownership review, GoDaddy staging verification, AI milestone absence, DPDP review, and Swiss Ephemeris licensing.

## 1.1.0 - 2026-11-15

- Added private Summary, Comprehensive, and Kundli Matching PDF generation with A4 layout, vector charts, page numbering, metadata, disclaimers, and no-store delivery.
- Added English, Hindi, and Punjabi translation catalogs with embedded OFL Noto Latin, Devanagari, and Gurmukhi fonts shaped through Pango/HarfBuzz.
- Reused D1, D9, D10, Panchang, Vimshottari Dasha, and Ashtakoota services without changing their formulas or storing redundant report data.
- Added `/reports` controls for profile, report type, language, sections, functional object-URL preview, and download.
- Added PDF structure, A4, localization, validation, frontend workflow tests, and visually inspected synthetic samples in all three languages.

## 1.0.0 - 2026-11-15

- Added pure Decimal-based Parashari Navamsha (D9) and Dashamsha (D10) transformations sourced from exact Step 6 Lahiri sidereal D1 longitudes.
- Added divisional Lagna, graha, whole-sign house, mean-node, Vargottama, exact-boundary, and proximity-warning metadata without duplicating stored chart data.
- Added typed ad-hoc, saved-profile, and configuration APIs with exact-time enforcement and development-only access to personal saved profiles.
- Added a responsive Divisional Charts workspace with D1/D9/D10 tabs, D1 comparison, accessible shared North Indian SVG rendering, tables, and per-chart SVG export.
- Added exhaustive tests for all 108 D9 and 120 D10 segments, documented examples, boundary behavior, API contracts, and regression coverage.
- Added calculation, method-specific, and external-reference documentation. No database migration was required.

## 0.9.0 - 2026-11-14

- Added a versioned Muhurta Chintamani North Indian Ashtakoota ruleset with complete Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, and Nadi scoring tables.
- Added explicit bride/groom calculation roles, exact Decimal totals out of 36, separate traditional observations, and neutral educational warnings.
- Reused Step 6 Lahiri sidereal Moon calculations for saved profiles and added safe unknown-time handling that rejects Moon Rashi or Nakshatra ambiguity.
- Added typed ad-hoc, saved-profile, configuration, and non-sensitive rules APIs with development-only restrictions for personal profile matching.
- Added a responsive Kundli Matching dashboard with searchable profile selectors, role controls, score visualization, eight-row breakdown, expandable explanations, and comparison details.
- Added exhaustive 729 Nakshatra-pair and 144 Rashi-pair checks, complete matrix tests, published-example comparisons, UI tests, and matching documentation.

## 0.8.0 - 2026-11-13

- Added a modular Vimshottari Dasha engine with the immutable nine-lord, 120-year sequence and precise birth-balance calculation from the Step 6 Lahiri sidereal Moon.
- Added complete theoretical Mahadasha, Antardasha, and Pratyantardasha hierarchies with half-open intervals and exact parent-end alignment.
- Added configurable 365.25-day and 360-day Savana conventions, UTC arithmetic, historical location-time rendering, and selected-instant current-period lookup.
- Added typed calculation, saved-profile, current-period, and configuration APIs with local-development restrictions on personal profile endpoints.
- Added a responsive Dasha dashboard with profile and convention controls, birth/current summaries, proportional keyboard-accessible timeline, expandable hierarchy, and educational context.
- Added focused backend/frontend tests, published-date and manual-formula comparisons, and calculation/reference documentation.

## 0.7.0 - 2026-11-13

- Added location-specific Swiss Ephemeris sunrise, sunset, and next-sunrise calculations with explicit polar-event handling.
- Added sunrise-anchored Drik Ganita Tithi, Paksha, Vara, Nakshatra/Pada, Yoga, and complete 60-position Karana calculations.
- Added a reusable wrap-safe transition solver and chronological sunrise-to-next-sunrise timeline.
- Added typed stored-location, coordinate, and configuration Panchang APIs with bounded input validation and explicit errors.
- Added a responsive Daily Panchang dashboard with location search, location-relative date navigation, five interactive cards, solar data, details, loading/retry states, and an accessible timeline.
- Added focused backend and frontend tests plus multi-city independent reference comparisons and calculation documentation.

## 0.6.0 - 2026-11-13

- Added a responsive SVG North Indian Janam Kundli with fixed houses and anticlockwise house progression.
- Added Standard and Detailed modes, Rashi and Lagna labels, retrograde notation, house details, synchronized graha selection, and standalone SVG export.
- Extended calculation responses with a typed twelve-house chart contract derived entirely from Step 6 Swiss Ephemeris results.
- Added keyboard-operable SVG houses and grahas, accessible names, focus styles, light/dark theme support, and mobile layouts.
- Added strict frontend chart-data validation and backend tests ensuring every graha is placed exactly once in a consistent house and Rashi.
- Added canonical geometry documentation and focused mapping, rendering, interaction, and control tests.

## 0.5.0 - 2026-11-13

- Added modular Julian Day, Lahiri ayanamsa, graha, Rashi, Nakshatra, Lagna, motion, and whole-sign house services.
- Added synchronized Swiss Ephemeris global-state handling and strict returned-flag validation to prevent silent source fallback.
- Added typed astrology configuration, ad-hoc calculation, and saved-profile calculation APIs.
- Added live-data Planetary Positions UI and a post-save Kundli calculation summary with unknown-time safeguards.
- Added 50 focused astrology tests, including every Rashi, every Nakshatra, all Padas, Julian Day precision, API validation, and a native-binding contract check.
- Selected `pyswisseph==2.10.3.2` with its established CPython 3.11 Windows wheel; Python 3.14 has no compatible wheel.
- Validated native import, Swiss Ephemeris 2.10.03, Lahiri ayanamsa, planetary positions, and sidereal ascendant calculations under Python 3.11.
- Documented the AGPL/professional dual-license decision gate; public deployment remains blocked.

## 0.4.0 - 2026-11-12

- Added complete birth-profile create, view, search, pagination, and update workflows.
- Added debounced, cancellable, keyboard-accessible stored-location search and controlled verified-location creation.
- Added gender preference, UTC-resolution metadata, timezone status, and DST fold fields through additive migration `20261112_02`.
- Added historical local-time resolution with `zoneinfo`/`tzdata`, including ambiguous and nonexistent daylight-saving handling.
- Added location search/filter/pagination/update APIs and safe protection for referenced coordinates/timezones.
- Added the birth-time validation API and nested location details in profile responses.
- Added saved-profile and profile-detail pages without implying that a Kundli has been calculated.
- Expanded backend tests to 28 and frontend tests to 17.

## 0.3.0 - 2026-11-12

- Refined the dashboard into a responsive saffron, maroon, and ivory portal.
- Added persistent light, dark, and system color themes.
- Added accessible desktop/sidebar and mobile navigation with active-route states.
- Added six honest feature cards, live service indicators, recent local profiles, and Jyotish education cards.
- Refined the birth-profile form with responsive fields, privacy guidance, and clearer feedback.
- Added a dedicated 404 route and centralized application text for multilingual readiness.
- Expanded UI coverage for navigation, mobile controls, themes, status, forms, and unknown routes.
- Added UI design and accessibility documentation.

## 0.2.0 - 2026-11-12

- Integrated MySQL 8.4 through SQLAlchemy 2, Alembic, and PyMySQL.
- Added users, locations, and birth profiles with constraints and relationships.
- Added database health, location CRUD, and birth-profile CRUD endpoints.
- Added isolated MySQL integration tests and IANA timezone validation.
- Added a live database indicator and development-only birth-profile form.

## 0.1.0 - 2026-11-11

- Added the React, TypeScript, Vite, and Tailwind CSS frontend foundation.
- Added a responsive dashboard and eight application routes.
- Added FastAPI health and version endpoints with development CORS.
- Added live backend-connectivity status with success and failure handling.
- Added Pytest and Vitest coverage plus local-development documentation.
