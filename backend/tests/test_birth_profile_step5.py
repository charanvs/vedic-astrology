from datetime import date, timedelta
from sqlalchemy import create_engine, delete, inspect
from sqlalchemy.orm import Session, sessionmaker
import pytest
from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.db.session import get_db
from app.main import create_app
from app.models import BirthProfile, Location, User
from tests.auth_helpers import authenticate

engine = create_engine(get_settings().database_url(test=True), pool_pre_ping=True)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
app = create_app()


def override_db():
    with TestingSession() as session:
        yield session


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    client.cookies.clear()
    with TestingSession() as db:
        db.execute(delete(BirthProfile)); db.execute(delete(Location)); db.execute(delete(User)); db.commit()
    authenticate(client,TestingSession,app)


def make_location(city="Chandigarh", state="Chandigarh", country="India", timezone="Asia/Kolkata", latitude=30.7333, longitude=76.7794):
    response = client.post("/api/locations", json={"city": city, "state": state, "country": country, "country_code": "IN" if country == "India" else None, "latitude": latitude, "longitude": longitude, "timezone": timezone})
    assert response.status_code == 201
    return response.json()


def profile_payload(location_id, **changes):
    payload = {"full_name": "Test Person", "gender": "prefer_not_to_say", "birth_date": "2000-01-15", "birth_time": "10:30:00", "birth_time_unknown": False, "location_id": location_id, "notes": "Synthetic test record"}
    payload.update(changes)
    return payload


def test_migration_has_additive_timezone_columns():
    columns = {column["name"] for column in inspect(engine).get_columns("birth_profiles")}
    assert {"gender", "birth_time_utc", "utc_offset_minutes", "timezone_resolution_status", "timezone_fold"} <= columns


def test_profile_create_read_update_search_and_pagination():
    location = make_location()
    created = client.post("/api/birth-profiles", json=profile_payload(location["id"]))
    assert created.status_code == 201
    body = created.json()
    assert body["birth_time"] == "10:30:00" and body["birth_time_utc"].startswith("2000-01-15T05:00:00")
    assert body["utc_offset_minutes"] == 330 and body["location"]["city"] == "Chandigarh"
    profile_id = body["id"]
    assert client.get(f"/api/birth-profiles/{profile_id}").status_code == 200
    updated = client.patch(f"/api/birth-profiles/{profile_id}", json={"full_name": "Updated Test Person", "notes": "Updated"})
    assert updated.status_code == 200 and updated.json()["full_name"] == "Updated Test Person"
    listed = client.get("/api/birth-profiles?search=Updated&offset=0&limit=1")
    assert listed.status_code == 200 and listed.headers["x-total-count"] == "1" and len(listed.json()) == 1


def test_unknown_birth_time_is_explicit_and_has_no_utc_guess():
    location = make_location()
    response = client.post("/api/birth-profiles", json=profile_payload(location["id"], birth_time=None, birth_time_unknown=True))
    body = response.json()
    assert response.status_code == 201
    assert body["birth_time"] is None and body["birth_time_utc"] is None and body["timezone_resolution_status"] == "unknown_time"


@pytest.mark.parametrize("timezone_name,birth_date,birth_time,offset,utc_fragment", [
    ("Asia/Kolkata", "2000-01-15", "10:30:00", 330, "05:00:00"),
    ("Europe/Berlin", "2000-01-15", "10:30:00", 60, "09:30:00"),
    ("America/Toronto", "2000-01-15", "10:30:00", -300, "15:30:00"),
])
def test_historical_timezone_conversion(timezone_name, birth_date, birth_time, offset, utc_fragment):
    response = client.post("/api/birth-time/validate", json={"birth_date": birth_date, "birth_time": birth_time, "timezone": timezone_name})
    assert response.status_code == 200
    body = response.json()
    assert body["resolution_status"] == "resolved" and body["utc_offset_minutes"] == offset and utc_fragment in body["utc_datetime"]


def test_ambiguous_time_requires_explicit_fold():
    payload = {"birth_date": "2023-11-05", "birth_time": "01:30:00", "timezone": "America/Toronto"}
    ambiguous = client.post("/api/birth-time/validate", json=payload)
    assert ambiguous.status_code == 200 and ambiguous.json()["resolution_status"] == "ambiguous"
    assert ambiguous.json()["utc_datetime"] is None and ambiguous.json()["candidate_offset_minutes"] == [-300, -240]
    resolved = client.post("/api/birth-time/validate", json={**payload, "fold": 1})
    assert resolved.status_code == 200 and resolved.json()["resolution_status"] == "resolved_ambiguous" and resolved.json()["utc_offset_minutes"] == -300


def test_nonexistent_daylight_saving_time_is_rejected():
    response = client.post("/api/birth-time/validate", json={"birth_date": "2023-03-12", "birth_time": "02:30:00", "timezone": "America/Toronto"})
    assert response.status_code == 422 and "does not exist" in response.json()["detail"]


def test_location_search_filters_pagination_and_safe_update():
    chandigarh = make_location()
    make_location("Ambala", "Haryana")
    make_location("Ambala", "Punjab")
    results = client.get("/api/locations?search=Ambala&state=Haryana&limit=1")
    assert results.status_code == 200 and results.headers["x-total-count"] == "1" and results.json()[0]["state"] == "Haryana"
    profile = client.post("/api/birth-profiles", json=profile_payload(chandigarh["id"]))
    assert profile.status_code == 201
    assert client.patch(f"/api/locations/{chandigarh['id']}", json={"city": "Chandigarh City"}).status_code == 200
    blocked = client.patch(f"/api/locations/{chandigarh['id']}", json={"timezone": "Europe/Berlin"})
    assert blocked.status_code == 409


def test_date_coordinate_timezone_and_reference_validation():
    assert client.post("/api/locations", json={"city": "Boundary", "country": "World", "latitude": -90, "longitude": 180, "timezone": "UTC"}).status_code == 201
    assert client.post("/api/locations", json={"city": "Bad", "country": "World", "latitude": -90.1, "longitude": 180.1, "timezone": "Bad/Zone"}).status_code == 422
    future = (date.today() + timedelta(days=1)).isoformat()
    assert client.post("/api/birth-profiles", json=profile_payload(999999, birth_date=future)).status_code == 422
    assert client.post("/api/birth-profiles", json=profile_payload(999999)).status_code == 422


def test_astrology_response_contains_valid_chart_ready_houses():
    location = make_location()
    profile = client.post("/api/birth-profiles", json=profile_payload(location["id"])).json()
    response = client.get(f"/api/astrology/birth-profiles/{profile['id']}/calculate")
    assert response.status_code == 200
    body = response.json()
    houses = body["houses"]
    assert len(houses) == 12
    assert [house["house_number"] for house in houses] == list(range(1, 13))
    lagna_rashi = body["lagna"]["rashi"]["number"]
    assert houses[0]["is_lagna"] is True and houses[0]["rashi_number"] == lagna_rashi
    assert [house["rashi_number"] for house in houses] == [
        ((lagna_rashi + house_number - 2) % 12) + 1
        for house_number in range(1, 13)
    ]
    placed = [planet for house in houses for planet in house["planet_identifiers"]]
    expected = [planet["identifier"] for planet in body["planets"]]
    assert sorted(placed) == sorted(expected) and len(placed) == len(set(placed)) == 9
    for planet in body["planets"]:
        assert planet["identifier"] in houses[planet["house"] - 1]["planet_identifiers"]
        assert planet["rashi"]["number"] == houses[planet["house"] - 1]["rashi_number"]
    rahu = next(planet for planet in body["planets"] if planet["identifier"] == "rahu")
    ketu = next(planet for planet in body["planets"] if planet["identifier"] == "ketu")
    assert (ketu["longitude"] - rahu["longitude"]) % 360 == pytest.approx(180.0)
    assert body["settings"]["ayanamsa_mode"] == "SIDM_LAHIRI"


def test_unknown_time_profile_cannot_generate_full_chart():
    location = make_location()
    profile = client.post("/api/birth-profiles", json=profile_payload(
        location["id"], birth_time=None, birth_time_unknown=True
    )).json()
    response = client.get(f"/api/astrology/birth-profiles/{profile['id']}/calculate")
    assert response.status_code == 422
    assert "Exact birth time" in response.json()["detail"]


def test_unicode_name_and_patch_does_not_null_unspecified_fields():
    location = make_location()
    created = client.post("/api/birth-profiles", json=profile_payload(location["id"], full_name="परीक्षण व्यक्ति"))
    assert created.status_code == 201
    updated = client.patch(f"/api/birth-profiles/{created.json()['id']}", json={"notes": "केवल टिप्पणी"})
    assert updated.status_code == 200 and updated.json()["full_name"] == "परीक्षण व्यक्ति" and updated.json()["birth_time"] == "10:30:00"
