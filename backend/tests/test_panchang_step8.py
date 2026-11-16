from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.astrology.config import get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.exceptions import EphemerisUnavailableError
from app.astrology.panchang import DailyPanchangService, PanchangInput
from app.astrology.panchang.constants import MOVABLE_KARANAS
from app.astrology.panchang.elements import (
    karana_for_elongation, karana_name, tithi_for_elongation,
    vara_for_instant, yoga_for_sum,
)
from app.astrology.panchang.sunrise import solar_event
from app.astrology.panchang.transitions import find_angular_transitions
from app.main import app


def chandigarh_input(day=date(2026, 11, 13)):
    return PanchangInput(day, 30.7333, 76.7794, "Asia/Kolkata", "Chandigarh", "Chandigarh", "India")


@pytest.mark.parametrize("number", range(1, 31))
def test_all_thirty_tithis_and_paksha(number):
    result = tithi_for_elongation((number - 1) * 12 + 1e-8)
    assert result["number"] == number
    assert result["paksha"] == ("Shukla Paksha" if number <= 15 else "Krishna Paksha")
    if number == 15:
        assert result["name"] == "Purnima"
    if number == 30:
        assert result["name"] == "Amavasya"


def test_tithi_wraparound():
    assert tithi_for_elongation(359.999999)["number"] == 30
    assert tithi_for_elongation(360.0)["number"] == 1


@pytest.mark.parametrize("number", range(1, 28))
def test_all_twenty_seven_yogas(number):
    assert yoga_for_sum((number - 1) * (360 / 27) + 1e-8)["number"] == number


def test_complete_sixty_position_karana_sequence():
    names = [karana_name(position) for position in range(60)]
    assert names[0] == "Kimstughna"
    assert names[1:8] == list(MOVABLE_KARANAS)
    assert names[50:57] == list(MOVABLE_KARANAS)
    assert names[57:] == ["Shakuni", "Chatushpada", "Naga"]
    assert {karana_name(position) for position in range(60)} == {
        "Kimstughna", "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
        "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga",
    }
    for position in range(60):
        assert karana_for_elongation(position * 6 + 1e-8)["position"] == position + 1


def test_transition_solver_handles_360_wrap_and_validates_sides():
    start = datetime(2026, 1, 1, tzinfo=UTC)
    def angle_at(value):
        return (359 + (value - start).total_seconds() / 3600 * 2) % 360
    transitions = find_angular_transitions(start, start + timedelta(hours=8), 6, angle_at, timedelta(hours=1))
    assert len(transitions) == 3
    first = transitions[0].at_utc
    assert abs((first - (start + timedelta(minutes=30))).total_seconds()) < 1
    assert angle_at(first - timedelta(seconds=1)) > 359.99
    assert angle_at(first + timedelta(seconds=1)) < 0.01


@pytest.mark.parametrize("weekday", range(7))
def test_all_varas_and_sunrise_boundary(weekday):
    local_date = date(2026, 11, 9) + timedelta(days=weekday)
    zone = ZoneInfo("Asia/Kolkata")
    sunrise = datetime.combine(local_date, datetime.min.time(), zone) + timedelta(hours=6)
    before = vara_for_instant(sunrise - timedelta(seconds=1), sunrise)
    after = vara_for_instant(sunrise + timedelta(seconds=1), sunrise)
    assert after["effective_date"] == local_date
    assert before["effective_date"] == local_date - timedelta(days=1)


@pytest.mark.parametrize("civil_date,latitude,longitude,timezone_name", [
    (date(2026, 3, 20), 51.5074, -0.1278, "Europe/London"),
    (date(2026, 7, 4), 40.7128, -74.0060, "America/New_York"),
    (date(2026, 11, 13), 30.7333, 76.7794, "Asia/Kolkata"),
])
def test_solar_events_match_requested_local_date(civil_date, latitude, longitude, timezone_name):
    zone = ZoneInfo(timezone_name)
    ephemeris = Ephemeris(get_calculation_settings())
    sunrise = solar_event(civil_date, zone, latitude, longitude, 0, "rise", ephemeris)
    sunset = solar_event(civil_date, zone, latitude, longitude, 0, "set", ephemeris)
    assert sunrise and sunrise.date() == civil_date and sunrise.tzinfo == zone
    assert sunset and sunset.date() == civil_date and sunset.tzinfo == zone
    assert sunrise < sunset


def test_high_latitude_missing_solar_event_is_explicit():
    zone = ZoneInfo("Europe/Oslo")
    ephemeris = Ephemeris(get_calculation_settings())
    assert solar_event(date(2026, 6, 21), zone, 78.2232, 15.6469, 0, "rise", ephemeris) is None


@pytest.fixture(scope="module")
def chandigarh_result():
    return DailyPanchangService().calculate(chandigarh_input())


def test_chandigarh_reference_values_and_transition_sides(chandigarh_result):
    result = chandigarh_result
    assert result["solar"]["sunrise"]["local"].strftime("%H:%M") == "06:47"
    assert result["solar"]["sunset"]["local"].strftime("%H:%M") == "17:26"
    assert result["tithi"]["display_name"] == "Shukla Chaturthi"
    assert result["tithi"]["end"]["local"].strftime("%H:%M") == "20:43"
    assert result["nakshatra"]["name"] == "Mula"
    assert result["nakshatra"]["pada"] == 3
    assert result["nakshatra"]["end"]["local"].strftime("%H:%M") == "17:17"
    assert result["yoga"]["name"] == "Dhriti"
    assert result["karana"]["name"] == "Vanija"
    assert result["vara"]["name"] == "Shukravara"
    assert len(result["timeline"]) >= 7
    assert "upper solar limb" in result["solar"]["convention"]


def test_daily_response_validates_against_pydantic(chandigarh_result):
    from app.schemas.panchang import DailyPanchangResponse
    validated = DailyPanchangResponse.model_validate(chandigarh_result)
    assert validated.tithi.number == 4
    assert validated.location.timezone == "Asia/Kolkata"


def test_coordinate_api_and_config():
    client = TestClient(app)
    response = client.post("/api/panchang/calculate", json={
        "date": "2026-11-13", "latitude": 30.7333, "longitude": 76.7794,
        "timezone": "Asia/Kolkata", "city": "Chandigarh", "state": "Chandigarh", "country": "India",
    })
    assert response.status_code == 200, response.text
    assert response.json()["tithi"]["display_name"] == "Shukla Chaturthi"
    config = client.get("/api/panchang/config")
    assert config.status_code == 200
    assert config.json()["method"] == "Drik Ganita"
    assert "path" not in config.text.lower()


def test_api_rejects_invalid_inputs_and_missing_sunrise():
    client = TestClient(app)
    invalid = client.post("/api/panchang/calculate", json={"date":"2026-01-01","latitude":91,"longitude":0,"timezone":"UTC"})
    assert invalid.status_code == 422
    timezone = client.post("/api/panchang/calculate", json={"date":"2026-01-01","latitude":0,"longitude":0,"timezone":"Not/AZone"})
    assert timezone.status_code == 422
    polar = client.post("/api/panchang/calculate", json={"date":"2026-06-21","latitude":78.2232,"longitude":15.6469,"timezone":"Europe/Oslo"})
    assert polar.status_code == 422
    assert "Sunrise is unavailable" in polar.json()["detail"]


def test_daily_api_rejects_unknown_location():
    client = TestClient(app)
    response = client.get(
        "/api/panchang/daily",
        params={"date": "2026-11-13", "location_id": 2_147_483_647},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Location not found"


def test_api_reports_missing_ephemeris_as_service_unavailable(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise EphemerisUnavailableError("Swiss Ephemeris native binding is unavailable")

    monkeypatch.setattr(DailyPanchangService, "calculate", unavailable)
    client = TestClient(app)
    response = client.post("/api/panchang/calculate", json={
        "date": "2026-11-13",
        "latitude": 30.7333,
        "longitude": 76.7794,
        "timezone": "Asia/Kolkata",
    })
    assert response.status_code == 503
    assert "native binding is unavailable" in response.json()["detail"]
