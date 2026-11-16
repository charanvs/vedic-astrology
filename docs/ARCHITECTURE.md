# Architecture

## Current foundation

The application is split into independently run services:

- `frontend/`: React and TypeScript single-page application built with Vite and styled with Tailwind CSS.
- `backend/`: FastAPI REST service with Pydantic response contracts.

During local development, Vite serves the browser application on port 5173 and proxies `/api` to FastAPI on port 8000. The frontend uses one Axios client so deployment routing can change without rewriting components.

## Astronomy calculation boundary

`backend/app/astrology/` contains database-independent algorithms and one synchronized facade around Swiss Ephemeris process-global state. Routes load validated profile/location data and delegate to `AstrologyCalculationService`; routes and React components contain no planetary mathematics. Results are calculated on demand and are not cached in MySQL.

The engine fixes the convention to geocentric sidereal positions, `SIDM_LAHIRI`, mean Rahu, derived opposite Ketu, and whole-sign houses from the actual sidereal ascendant Rashi. The requested ephemeris source is environment-driven and returned flags are checked so Moshier fallback cannot masquerade as Swiss data files.

## Production deployment

The planned public path is `https://cvstudy.in/vedic-astrology/`. Production Vite assets and React Router use `/vedic-astrology/` as their base. The web server will need an SPA fallback for routes such as `/vedic-astrology/kundli`.

GoDaddy is known to support Python applications on the account, but its exact ASGI/WSGI startup arrangement, reverse-proxy behavior, process lifecycle, and subpath routing must be verified before deployment. Deployment must not alter the existing `cvstudy.in` website.
