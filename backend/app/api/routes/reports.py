import logging
from importlib.metadata import version

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.reports.config import FONT_ROOT, REPORT_VERSION, SUPPORTED_LANGUAGES, SUPPORTED_REPORTS, SUPPORTED_SECTIONS
from app.reports.generator import FONT_FILES, KundliReportService, PdfRendererUnavailable, ReportGenerationError, pdf_renderer_available
from app.reports.localization import MissingTranslationError
from app.reports.schemas import KundliReportRequest, MatchingReportRequest
from app.core.security import rate_limit, require_csrf
from app.models import BirthProfile
from sqlalchemy import func, select

router=APIRouter(prefix="/reports",tags=["PDF reports"])
logger=logging.getLogger(__name__)

def pdf_response(pdf: bytes, filename: str, inline: bool=False):
    disposition="inline" if inline else "attachment"
    return Response(pdf,media_type="application/pdf",headers={"Content-Disposition":f'{disposition}; filename="{filename}"',"Cache-Control":"no-store, private","X-Content-Type-Options":"nosniff"})

def generate(action):
    try: return action()
    except HTTPException: raise
    except PdfRendererUnavailable as exc:
        logger.error("PDF renderer unavailable: %s", exc.__cause__)
        raise HTTPException(503,str(exc)) from exc
    except (ValueError,MissingTranslationError,ReportGenerationError) as exc: raise HTTPException(422,str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF report generation failed")
        raise HTTPException(503,"PDF report generation failed") from exc
def ensure_owned(db:Session,user_id:int,*profile_ids:int):
    count=db.scalar(select(func.count(BirthProfile.id)).where(BirthProfile.id.in_(profile_ids),BirthProfile.user_id==user_id)) or 0
    if count!=len(set(profile_ids)):raise HTTPException(404,"Birth profile not found")

@router.get("/config")
def report_config():
    return {"report_version":REPORT_VERSION,"report_types":SUPPORTED_REPORTS,"languages":SUPPORTED_LANGUAGES,"sections":SUPPORTED_SECTIONS,"renderer":{"name":"WeasyPrint","version":version("weasyprint"),"complex_text":"Pango/HarfBuzz","vector_svg":True,"available":pdf_renderer_available()},"public_deployment_blocked":False}

@router.post("/kundli")
def kundli_report(payload: KundliReportRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
    ensure_owned(db,context.user.id,payload.profile_id);rate_limit(db,request,"pdf",10,3600,str(context.user.id));pdf,filename=generate(lambda:KundliReportService().kundli(db,payload));return pdf_response(pdf,filename)

@router.post("/preview")
def preview_report(payload: KundliReportRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
    ensure_owned(db,context.user.id,payload.profile_id);rate_limit(db,request,"pdf",10,3600,str(context.user.id));pdf,filename=generate(lambda:KundliReportService().kundli(db,payload));return pdf_response(pdf,filename,True)

@router.post("/matching")
def matching_report(payload: MatchingReportRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
    ensure_owned(db,context.user.id,payload.partner_one_profile_id,payload.partner_two_profile_id);rate_limit(db,request,"pdf",10,3600,str(context.user.id));pdf,filename=generate(lambda:KundliReportService().matching(db,payload));return pdf_response(pdf,filename)

def printable_response(html: str):
    return HTMLResponse(html,headers={"Cache-Control":"no-store, private","X-Content-Type-Options":"nosniff"})

@router.post("/kundli/printable",response_class=HTMLResponse)
def kundli_printable(payload: KundliReportRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
    """The same report as a print-ready web page, for servers that cannot render PDFs."""
    ensure_owned(db,context.user.id,payload.profile_id);rate_limit(db,request,"pdf",10,3600,str(context.user.id))
    html,_=generate(lambda:KundliReportService().kundli(db,payload,output="html"));return printable_response(html)

@router.post("/matching/printable",response_class=HTMLResponse)
def matching_printable(payload: MatchingReportRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
    ensure_owned(db,context.user.id,payload.partner_one_profile_id,payload.partner_two_profile_id);rate_limit(db,request,"pdf",10,3600,str(context.user.id))
    html,_=generate(lambda:KundliReportService().matching(db,payload,output="html"));return printable_response(html)

@router.get("/fonts/{name}")
def report_font(name: str):
    """The bundled Noto fonts (SIL OFL), so printable reports render Hindi and Punjabi correctly."""
    if name not in FONT_FILES: raise HTTPException(404,"Font not found")
    return FileResponse(FONT_ROOT/name,media_type="font/ttf",headers={"Cache-Control":"public, max-age=2592000"})
