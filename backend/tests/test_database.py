import os
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,delete,text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session,sessionmaker
from app.core.config import get_settings
from app.db.session import get_db
from app.main import create_app
from app.models import BirthProfile,Location,User
from tests.auth_helpers import authenticate

engine=create_engine(get_settings().database_url(test=True),pool_pre_ping=True)
TestingSession=sessionmaker(bind=engine,expire_on_commit=False)
app=create_app()
def override_db()->Generator[Session,None,None]:
 with TestingSession() as session:yield session
app.dependency_overrides[get_db]=override_db
client=TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
 client.cookies.clear()
 with TestingSession() as db:
  db.execute(delete(BirthProfile));db.execute(delete(Location));db.execute(delete(User));db.commit()
 authenticate(client,TestingSession,app)

def location_payload(**changes):
 data={"city":"Chandigarh","state":"Chandigarh","country":"India","country_code":"IN","latitude":30.7333,"longitude":76.7794,"timezone":"Asia/Kolkata"};data.update(changes);return data
def create_location(**changes):return client.post("/api/locations",json=location_payload(**changes))

def test_database_connection_session_and_migration():
 with TestingSession() as db:
  assert db.scalar(text("SELECT 1"))==1
  assert db.scalar(text("SELECT version_num FROM alembic_version"))=="20261116_01"
 assert client.get("/api/db-health").json()=={"status":"ok","database":"connected"}

def test_valid_indian_international_and_unicode_locations():
 assert create_location().status_code==201
 assert create_location(city="München",state="Bayern",country="Germany",country_code="de",latitude=48.1351,longitude=11.5820,timezone="Europe/Berlin").status_code==201
 assert create_location(city="ਅੰਮ੍ਰਿਤਸਰ").status_code==201
 assert len(client.get("/api/locations?limit=2").json())==2

@pytest.mark.parametrize("changes",[{"latitude":91},{"longitude":181},{"timezone":"Mars/Olympus"}])
def test_invalid_location_values(changes):assert create_location(**changes).status_code==422

def test_missing_location_fields():assert client.post("/api/locations",json={"city":"Nowhere"}).status_code==422

def test_birth_profile_crud_unicode_and_pagination():
 location_id=create_location().json()["id"]
 payload={"full_name":"ਟੈਸਟ ਵਿਅਕਤੀ","birth_date":"2000-01-15","birth_time":"10:30:00","birth_time_unknown":False,"location_id":location_id}
 created=client.post("/api/birth-profiles",json=payload);assert created.status_code==201
 profile_id=created.json()["id"];assert client.get(f"/api/birth-profiles/{profile_id}").status_code==200
 updated=client.patch(f"/api/birth-profiles/{profile_id}",json={"full_name":"परीक्षण व्यक्ति"});assert updated.status_code==200
 assert client.get("/api/birth-profiles?offset=0&limit=1").json()[0]["full_name"]=="परीक्षण व्यक्ति"

def test_unknown_time_and_missing_location():
 location_id=create_location().json()["id"]
 unknown=client.post("/api/birth-profiles",json={"full_name":"Test Person","birth_date":"2000-01-15","birth_time_unknown":True,"location_id":location_id});assert unknown.status_code==201 and unknown.json()["birth_time"] is None
 missing=client.post("/api/birth-profiles",json={"full_name":"Test","birth_date":"2000-01-15","birth_time":"10:00:00","location_id":999999});assert missing.status_code==422

def test_invalid_profile_and_missing_id():
 location_id=create_location().json()["id"]
 assert client.post("/api/birth-profiles",json={"full_name":"Test","birth_date":"bad","birth_time":"bad","location_id":location_id}).status_code==422
 assert client.get("/api/birth-profiles/999999").status_code==404

def test_foreign_key_integrity():
 with TestingSession() as db:
  db.add(BirthProfile(full_name="Invalid",birth_date="2000-01-01",birth_time="10:00:00",birth_time_unknown=False,location_id=999999))
  with pytest.raises(Exception):db.commit()

def test_database_failure_returns_503():
 class Broken:
  def execute(self,*_):raise OperationalError("statement",{},Exception("offline"))
 def broken_db():yield Broken()
 app.dependency_overrides[get_db]=broken_db
 try:assert client.get("/api/db-health").status_code==503
 finally:app.dependency_overrides[get_db]=override_db
