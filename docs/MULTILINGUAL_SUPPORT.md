# Multilingual Report Support

Report labels and disclaimers are centralized in complete `en`, `hi`, and `pa` JSON catalogs. Punjabi uses Gurmukhi and is never substituted with Hindi. Missing keys fail report generation instead of silently mixing an incomplete catalog.

Bundled Noto Sans, Noto Sans Devanagari, and Noto Sans Gurmukhi fonts are licensed under SIL Open Font License 1.1; the included `OFL.txt` applies. WeasyPrint uses Pango/HarfBuzz shaping and subsets embedded fonts. Technical astronomical values remain identical across languages.

Scope is the reports page and generated reports. Other application pages are not claimed to be fully localized.
