import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REPORT_VERSION = "1.0.0"
REPORT_ROOT = Path(__file__).resolve().parent
TEMPLATE_ROOT = REPORT_ROOT / "templates"
STYLE_ROOT = REPORT_ROOT / "styles"
TRANSLATION_ROOT = REPORT_ROOT / "translations"
INTERPRETATION_ROOT = REPORT_ROOT / "interpretations"
FONT_ROOT = REPORT_ROOT / "fonts"
MAX_PDF_BYTES = int(os.getenv("PDF_MAX_BYTES", "10485760"))
SUPPORTED_LANGUAGES = {"en": "English", "hi": "हिन्दी", "pa": "ਪੰਜਾਬੀ"}
SUPPORTED_REPORTS = {"summary": "Summary Kundli", "comprehensive": "Comprehensive Kundli", "matching": "Kundli Matching"}
SUPPORTED_SECTIONS = ("birth_details", "d1_chart", "planetary_positions", "d9_chart", "d10_chart", "panchang", "dasha", "interpretation", "forecast", "calculation_notes")

_dll_handles = []
for directory in filter(None, os.getenv("PDF_DLL_DIRECTORIES", "").split(os.pathsep)):
    if os.name == "nt" and Path(directory).is_dir():
        _dll_handles.append(os.add_dll_directory(directory))
os.environ.setdefault("WEASYPRINT_DLL_DIRECTORIES", os.getenv("PDF_DLL_DIRECTORIES", ""))
