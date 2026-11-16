# PDF Rendering Deployment

## Renderer decision

WeasyPrint was selected because it supports paged CSS, automatic font embedding, Pango/HarfBuzz complex-text shaping, and vector SVG. Local Windows uses MSYS2 Pango 1.56.4 through the `PDF_DLL_DIRECTORIES` environment variable.

Linux requires Pango, Fontconfig, HarfBuzz (including subset support), and their runtime libraries before installing Python requirements. GoDaddy shared Python support does not prove these native packages can be installed. Server-side PDF activation is therefore blocked until GoDaddy confirms them and a staging render passes.

If native libraries are unavailable, the documented fallback is authenticated browser print using the same printable HTML and bundled fonts. It must be implemented and validated at deployment time; the application must not silently emit PDFs with broken scripts. No Windows path is present in source code, and the DLL directory is environment-configured.
