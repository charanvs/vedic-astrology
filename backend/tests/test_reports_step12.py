from datetime import date, datetime, time
from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pypdf import PdfReader

from app.main import app
from app.reports.generator import KundliReportService
from app.reports.localization import MissingTranslationError, catalog, translator
from app.reports.schemas import KundliReportRequest, MatchingReportRequest


def synthetic_profile():
    location=SimpleNamespace(id=0,city="Chandigarh",state="Chandigarh",country="India",latitude=30.7333,longitude=76.7794,timezone="Asia/Kolkata")
    return SimpleNamespace(id=0,full_name="Synthetic व्यक्ति ਵਿਅਕਤੀ",birth_date=date(2000,1,15),birth_time=time(10,30),birth_time_unknown=False,birth_time_utc=datetime(2000,1,15,5,0),timezone_resolution_status="resolved",location=location)


@pytest.mark.parametrize("language",["en","hi","pa"])
def test_summary_pdf_languages_are_valid_a4(language):
    pdf,_=KundliReportService().kundli_for_profile(synthetic_profile(),KundliReportRequest(profile_id=1,language=language,sections=["birth_details","d1_chart","planetary_positions","calculation_notes"]))
    assert pdf.startswith(b"%PDF-") and len(pdf)<10*1024*1024
    reader=PdfReader(BytesIO(pdf)); assert len(reader.pages)==5
    assert float(reader.pages[0].mediabox.width)==pytest.approx(595.276,abs=1)


def test_translation_catalogs_are_complete_and_complex_scripts_present():
    keys=set(catalog("en")); assert keys==set(catalog("hi"))==set(catalog("pa"))
    assert "कुंडली" in translator("hi")("report_title")
    assert "ਕੁੰਡਲੀ" in translator("pa")("report_title")
    with pytest.raises(MissingTranslationError): translator("en")("missing.key")


def test_report_schemas_reject_unsafe_or_inconsistent_inputs():
    with pytest.raises(ValidationError): KundliReportRequest(profile_id=0,language="fr")
    with pytest.raises(ValidationError): KundliReportRequest(profile_id=1,sections=["d1_chart","d1_chart"])
    with pytest.raises(ValidationError): MatchingReportRequest(partner_one_profile_id=1,partner_two_profile_id=1,partner_one_role="bride",partner_two_role="groom")


def test_report_config_is_public_metadata_only():
    response=TestClient(app).get("/api/reports/config")
    assert response.status_code==200
    body=response.json(); assert body["renderer"]["name"]=="WeasyPrint" and body["languages"]["hi"]=="हिन्दी"
    assert "path" not in str(body).lower() and body["public_deployment_blocked"] is False and body["renderer"]["available"] is True
