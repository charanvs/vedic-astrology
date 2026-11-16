# Swiss Ephemeris License Decision Gate

Swiss Ephemeris and its Python bindings use a dual-license model:

1. GNU Affero General Public License version 3.
2. Swiss Ephemeris Professional License purchased from Astrodienst.

Astrodienst states that the choice must be made before distributing software containing Swiss Ephemeris or activating a public service, and that the AGPL route requires the whole project to use AGPL or a compatible license. Server-side use does not remove the network-source obligations of the AGPL.

Authoritative source: [Astrodienst Swiss Ephemeris licensing](https://www.astro.com/swisseph/swephinfo_e.htm).

## Current decision

**Decided 2026-11-16 by the owner: AGPL route (Swiss Ephemeris Free Edition).** The complete application is released under the GNU Affero General Public License v3 or later (`LICENSE` in the repository root), and `public_deployment_blocked` is now false in API metadata.

How the corresponding-source obligation is met:

- The application footer links to `/astrology/api/source`, which redirects to the public repository configured by `SOURCE_CODE_URL`.
- `deploy/check_server.py` warns while `SOURCE_CODE_URL` is unset; the site should not be announced until it is set.
- Each deployed version must have its matching source published (see `docs/DEPLOYMENT_GODADDY.md`).
- Secrets are never part of the source: `.env` files, database dumps and build output are excluded by `.gitignore`.

Bundled third-party material keeps its own terms: Noto fonts (SIL OFL 1.1, `backend/app/reports/fonts/OFL.txt`) and GeoNames city data (CC BY 4.0, attributed in the footer).

This document records a technical release gate, not legal advice. The final choice should be reviewed with qualified counsel or directly with Astrodienst.

## Additional deployment controls

- Preserve all required license notices and package source offers.
- Confirm whether ephemeris data files have separate distribution conditions.
- Record package and engine versions in every calculation.
- Keep the production engine disabled until authentication, profile ownership, and transport security are implemented.
