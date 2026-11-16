from datetime import date, datetime, time
from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from app.reports.generator import KundliReportService
from app.reports.schemas import KundliReportRequest

location=SimpleNamespace(id=0,city="Chandigarh",state="Chandigarh",country="India",latitude=30.7333,longitude=76.7794,timezone="Asia/Kolkata")
profile=SimpleNamespace(id=0,full_name="Synthetic Test Person",birth_date=date(2000,1,15),birth_time=time(10,30),birth_time_unknown=False,birth_time_utc=datetime(2000,1,15,5,0),timezone_resolution_status="resolved",location=location)
root=Path(__file__).resolve().parents[2]/"output"/"pdf"; root.mkdir(parents=True,exist_ok=True)
service=KundliReportService()
for language,report_type in (("en","summary"),("hi","comprehensive"),("pa","comprehensive")):
    payload=KundliReportRequest(profile_id=1,report_type=report_type,language=language,reference_datetime="2026-11-15T00:00:00+00:00")
    pdf,_=service.kundli_for_profile(profile,payload)
    path=root/f"step12-synthetic-{language}.pdf"; path.write_bytes(pdf); print(path.name,len(pdf))
