# Divisional Charts

Step 11 derives D9 Navamsha and D10 Dashamsha from the high-precision sidereal longitudes produced by the Step 6 Swiss Ephemeris service. It never recalculates planets independently and stores no redundant chart rows.

## Contract

- Zodiac: sidereal
- Ayanamsa: Lahiri (Chitrapaksha)
- Nodes: mean Rahu and exactly opposite Ketu
- Reference: geocentric planets; sidereal ascendant for Lagna
- Houses: whole-sign from the transformed divisional Lagna
- Required time: exact, timezone-resolved birth time
- Interval rule: half-open `[start, end)`; an exact boundary belongs to the next division

The one-arcminute boundary warning is informational. It does not shift the longitude or change the selected segment. Since D9/D10 Lagna can change quickly, users should verify rounded birth times.

## API and UI

`POST /api/divisional/calculate` accepts birth coordinates and `chart_type` (`D9` or `D10`). Saved-profile routes are `GET /api/divisional/birth-profiles/{id}/d9` and `/d10`; they remain restricted to local development until authentication and ownership controls exist. `GET /api/divisional/config` exposes non-sensitive method metadata.

The `/divisional-charts` page offers D1, D9, and D10 tabs. D9/D10 views place the selected divisional chart beside D1 on wide screens and stack them on smaller screens. The existing North Indian chart component is reused with unique accessible SVG labels and standalone export metadata.

## Error policy

Unknown, ambiguous, or unresolved birth times are rejected rather than invented. Missing Swiss Ephemeris support returns service-unavailable. Unsupported chart types and invalid coordinates return validation errors. No predictive interpretation is generated.
