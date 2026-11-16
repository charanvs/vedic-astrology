# UI design system

## Direction

The Step 4 interface uses a restrained Vedic-inspired palette without presenting decorative symbolism as astrological output. Saffron is the primary action color, maroon anchors the welcome panel, ivory provides the main background, and neutral borders keep content readable. The layout remains a development portal until authentication and calculation features are implemented.

## Theme tokens

Shared CSS variables in `frontend/src/styles/index.css` define the primary, surface, background, text, muted, border, and soft colors. Components use these semantic variables instead of duplicating fixed colors. Light, dark, and operating-system themes are available from the header and the preference is stored in `localStorage` under `vedic-theme`.

The initial theme script in `frontend/index.html` applies the stored preference before React starts, reducing theme flash. System mode also responds to operating-system preference changes while the page is open.

## Layout and responsiveness

- The header remains visible while scrolling and contains branding, the mobile navigation trigger, theme control, and settings shortcut.
- The navigation is a fixed drawer below the `lg` breakpoint and a sticky sidebar at larger sizes.
- Dashboard cards use one, two, or three columns according to available width.
- Form fields use one column on narrow screens and two columns when space permits.
- Interactive controls have a minimum height of 40–48 pixels and visible keyboard focus.

## Accessibility

- Navigation landmarks and control labels identify their purpose to assistive technology.
- Active routes have both React Router state and a visible color treatment.
- Backend, database, form-error, and save-result regions announce state changes.
- Text and interactive colors are selected for legibility in both themes.
- Reduced-motion preferences disable nonessential animation and transition duration.
- Icons are supplementary; essential meaning is also expressed in text.

## Content and localization readiness

Application identity and welcome copy are centralized in `frontend/src/constants/ui.ts`. Future multilingual work should move the remaining route, feature, form, and education strings into the same translation layer. The font stack already includes Devanagari and Gurmukhi-compatible fallbacks when installed on the device.

## Product-state honesty

Only birth-profile storage is marked available. Panchang, planetary positions, Dasha, matching, saved-chart workflows, and astrology calculations remain explicitly labeled as coming soon or under development. Dashboard status values come from the actual FastAPI and MySQL health endpoints.

## Deployment boundary

The Vite production base remains `/vedic-astrology/`. Any future server configuration must provide an SPA fallback under that subpath without changing the existing `cvstudy.in` site. Local and production databases must remain separate.
