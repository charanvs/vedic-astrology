from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup
from pypdf import PdfReader

from app.reports import config
from app.reports.calculations import collect_kundli, collect_matching, load_profile
from app.reports.charts import kundli_svg
from app.reports.interpretation import build_forecast, build_house_readings, build_interpretation, build_matching_interpretation
from app.reports.localization import translator
from app.core.config import get_settings

DEFAULT_SUMMARY={"birth_details","d1_chart","planetary_positions","interpretation","forecast","calculation_notes"}
DEFAULT_COMPREHENSIVE={"birth_details","d1_chart","planetary_positions","d9_chart","d10_chart","panchang","dasha","interpretation","forecast","calculation_notes"}

FONT_FILES = {"NotoSans.ttf", "NotoSansDevanagari.ttf", "NotoSansGurmukhi.ttf"}

class ReportGenerationError(RuntimeError): pass
class PdfRendererUnavailable(RuntimeError): pass

def pdf_renderer_problem() -> str | None:
    """Why server-side PDFs cannot be rendered here, or None. WeasyPrint needs Pango 1.44+;
    an older system Pango still imports and only fails mid-render, so check its version."""
    try:
        from weasyprint.text.ffi import pango
        found = pango.pango_version()
    except (ImportError, OSError, AttributeError) as exc: return f"{type(exc).__name__}: {exc}"
    if found < 14400: return f"system Pango {found // 10000}.{found // 100 % 100}.{found % 100} is older than the required 1.44"
    return None

def pdf_renderer_available() -> bool:
    return pdf_renderer_problem() is None

def website() -> str:
    return get_settings().public_url.rstrip("/")+"/"

class KundliReportService:
    def __init__(self):
        self.environment=Environment(loader=FileSystemLoader(config.TEMPLATE_ROOT),undefined=StrictUndefined,autoescape=select_autoescape(("html",)))

    @staticmethod
    def _validate(pdf: bytes):
        if not pdf.startswith(b"%PDF-"): raise ReportGenerationError("Renderer did not return a valid PDF")
        if len(pdf)>config.MAX_PDF_BYTES: raise ReportGenerationError("Generated PDF exceeds the configured size limit")
        reader=PdfReader(BytesIO(pdf))
        if not reader.pages: raise ReportGenerationError("Generated PDF has no pages")
        for page in reader.pages:
            width,height=float(page.mediabox.width),float(page.mediabox.height)
            if abs(width-595.28)>3 or abs(height-841.89)>3: raise ReportGenerationError("Generated PDF is not A4 portrait")

    def _html(self, context: dict, printable: bool) -> str:
        css=None
        if printable:
            fonts=get_settings().base_path.rstrip("/")+"/api/reports/fonts/"
            css=Markup((config.STYLE_ROOT/"report.css").read_text(encoding="utf-8").replace("url('../fonts/",f"url('{fonts}"))
        label=context["website"].split("://",1)[-1].rstrip("/")
        return self.environment.get_template("report.html").render(website_label=label,inline_css=css,printable=printable,**context)

    def _render(self, context: dict, output: str = "pdf") -> bytes | str:
        if output=="html": return self._html(context,printable=True)
        if problem:=pdf_renderer_problem(): raise PdfRendererUnavailable("PDF reports are not available on this server yet") from RuntimeError(problem)
        from weasyprint import HTML
        pdf=HTML(string=self._html(context,printable=False),base_url=str(config.REPORT_ROOT)).write_pdf()
        self._validate(pdf)
        return pdf

    def kundli(self, db, payload, output: str = "pdf") -> tuple[bytes|str,str]:
        profile=load_profile(db,payload.profile_id)
        return self.kundli_for_profile(profile,payload,output)

    def kundli_for_profile(self, profile, payload, output: str = "pdf") -> tuple[bytes|str,str]:
        defaults=DEFAULT_SUMMARY if payload.report_type=="summary" else DEFAULT_COMPREHENSIVE
        sections=set(payload.sections) if payload.sections is not None else defaults
        if not sections: raise ReportGenerationError("At least one report section must be selected")
        values=collect_kundli(profile,payload.report_type,sections,payload.dasha_year_convention,payload.reference_datetime)
        t=translator(payload.language); generated=datetime.now(UTC)
        context={"kind":"kundli","report_type":payload.report_type,"language":payload.language,"t":t,"profile":profile,"sections":sections,"generated":generated,"website":website(),**values}
        context["charts"]={"d1":Markup(kundli_svg(values["d1"],t("d1")))}
        if "d9" in values: context["charts"]["d9"]=Markup(kundli_svg(values["d9"],t("d9")))
        if "d10" in values: context["charts"]["d10"]=Markup(kundli_svg(values["d10"],t("d10")))
        if "interpretation" in sections:
            context["interpretation"]=build_interpretation(values["d1"],values["dasha"],payload.language)
            context["house_readings"]=build_house_readings(values["d1"],payload.language)
        if "forecast" in sections:
            context["forecast"]=build_forecast(values["d1"],values["dasha"],values["transits"],values["forecast_window"],profile.location.timezone,payload.language)
        return self._render(context,output),f"kundli-{payload.report_type}-profile-{profile.id}-{payload.language}.pdf"

    def matching(self, db, payload, output: str = "pdf") -> tuple[bytes|str,str]:
        first,second,result=collect_matching(db,payload.partner_one_profile_id,payload.partner_two_profile_id,payload.partner_one_role,payload.partner_two_role,payload.ruleset)
        context={"kind":"matching","language":payload.language,"t":translator(payload.language),"first":first,"second":second,"matching":result,"matching_interpretation":build_matching_interpretation(result,payload.language),"generated":datetime.now(UTC),"website":website()}
        return self._render(context,output),f"kundli-matching-{first.id}-{second.id}-{payload.language}.pdf"
