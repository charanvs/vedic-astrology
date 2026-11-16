# PDF Reports

Version 1.1.0 provides Summary Kundli, Comprehensive Kundli, and separate Kundli Matching reports. The service gathers data from the existing D1, D9, D10, Panchang, Dasha, and Matching engines; it does not implement independent astrology formulas.

WeasyPrint 70 renders reusable Jinja HTML/CSS templates to A4 PDF. Canonical North Indian house geometry is emitted as vector SVG. Output is generated in memory, checked for a PDF signature, page presence, A4 dimensions, and a 10 MiB limit, then returned with `application/pdf`, safe ASCII filenames, `nosniff`, and private no-store headers.

Endpoints: `POST /api/reports/kundli`, `/preview`, `/matching`, and `GET /api/reports/config`. Personal endpoints are development-only. The React `/reports` page uses revocable object URLs for preview and download.
