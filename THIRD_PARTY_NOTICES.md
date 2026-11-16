# Third-party notices

This application is licensed under the GNU Affero General Public License v3 or later (see `LICENSE`). It includes or depends on the following third-party material, each under its own terms.

## Swiss Ephemeris

Planetary positions are calculated with the Swiss Ephemeris, Copyright (C) 1997–2026 Astrodienst AG, Switzerland, used through the `pyswisseph` Python binding. Both are used under the GNU Affero General Public License (the Swiss Ephemeris Free Edition). The calculations use the built-in Moshier ephemeris, so no separate ephemeris data files are distributed.

- Swiss Ephemeris: https://www.astro.com/swisseph/
- pyswisseph: https://github.com/astrorigin/pyswisseph

Because this is the AGPL edition, anyone who uses the hosted application can get its complete source code through the **Source code** link in the site footer (`/api/source`).

## GeoNames city data

`backend/app/data/geocoding_cities.csv` is derived from the GeoNames geographical database (`cities15000`, `admin1CodesASCII`, `countryInfo`). The data is licensed under Creative Commons Attribution 4.0 (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

Changes made: the data was reduced to name, state, country, coordinates, time zone and population. `backend/scripts/build_geocoding_dataset.py` rebuilds it from a GeoNames export.

Source: GeoNames, https://www.geonames.org/

## Noto fonts

`backend/app/reports/fonts/NotoSans.ttf`, `NotoSansDevanagari.ttf` and `NotoSansGurmukhi.ttf` are Noto fonts, Copyright the Noto Project Authors, licensed under the SIL Open Font License 1.1. The full licence text is in `backend/app/reports/fonts/OFL.txt`.

## Software dependencies

The backend's Python packages are listed in `backend/requirements.txt` and `backend/requirements-production.txt`. The frontend's JavaScript packages are listed in `frontend/package.json` and `frontend/package-lock.json`. Each package keeps its own licence. They are installed from PyPI and npm, not copied into this repository.
