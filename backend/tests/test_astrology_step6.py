from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.astrology.exceptions import EphemerisUnavailableError, UnsupportedDateError
from app.astrology.julian import utc_to_julian_day
from app.astrology.nakshatra import NAKSHATRA_SPAN, PADA_SPAN, nakshatra_for_longitude
from app.astrology.planets import motion_from_speed
from app.astrology.rashi import rashi_for_longitude, whole_sign_house, whole_sign_houses
from app.main import app


def test_j2000_reference_and_seconds_precision():
    # USNO/IAU J2000.0 definition: 2000-01-01 12:00 UT = JD 2451545.0.
    instant = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
    assert utc_to_julian_day(instant).julian_day_ut == pytest.approx(2451545.0, abs=1e-9)
    later = utc_to_julian_day(instant + timedelta(seconds=1, microseconds=500_000))
    assert later.julian_day_ut - 2451545.0 == pytest.approx(1.5 / 86400.0, abs=1e-9)


def test_julian_rollover_leap_year_and_validation():
    before = utc_to_julian_day(datetime(2024, 2, 29, 23, 59, 59, tzinfo=UTC)).julian_day_ut
    after = utc_to_julian_day(datetime(2024, 3, 1, 0, 0, 0, tzinfo=UTC)).julian_day_ut
    assert after - before == pytest.approx(1 / 86400, abs=1e-9)
    with pytest.raises(UnsupportedDateError):
        utc_to_julian_day(datetime(1599, 12, 31, tzinfo=UTC))
    with pytest.raises(UnsupportedDateError):
        utc_to_julian_day(datetime(2000, 1, 1))


@pytest.mark.parametrize("index", range(12))
def test_all_rashis_and_exact_boundaries(index):
    start = index * 30.0
    result = rashi_for_longitude(start)
    assert result["number"] == index + 1
    assert result["longitude_within"] == pytest.approx(0.0)
    near_end = rashi_for_longitude(start + 29.999999999)
    assert near_end["number"] == index + 1


def test_rashi_normalization_and_whole_sign_houses():
    assert rashi_for_longitude(360.0)["number"] == 1
    assert rashi_for_longitude(-0.1)["number"] == 12
    assert whole_sign_house(1, 1) == 1
    assert whole_sign_house(12, 1) == 12
    assert whole_sign_house(1, 12) == 2
    houses = whole_sign_houses(5)
    assert houses[0] == {"house": 1, "rashi": 5}
    assert houses[-1] == {"house": 12, "rashi": 4}


@pytest.mark.parametrize("index", range(27))
def test_all_nakshatras_lords_and_boundaries(index):
    result = nakshatra_for_longitude(index * NAKSHATRA_SPAN)
    assert result["number"] == index + 1
    assert result["lord"] in {"Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"}
    assert nakshatra_for_longitude(index * NAKSHATRA_SPAN + NAKSHATRA_SPAN - 1e-10)["number"] == index + 1


@pytest.mark.parametrize("pada", [1, 2, 3, 4])
def test_all_nakshatra_padas(pada):
    longitude = (pada - 1) * PADA_SPAN + 1e-9
    assert nakshatra_for_longitude(longitude)["pada"] == pada


def test_motion_classification_threshold():
    assert motion_from_speed(0.2, 0.0001) == "direct"
    assert motion_from_speed(-0.2, 0.0001) == "retrograde"
    assert motion_from_speed(0.00005, 0.0001) == "stationary"


def test_astrology_config_is_safe_when_engine_is_unavailable(monkeypatch):
    from app.api.routes import astrology
    monkeypatch.setattr(
        astrology.Ephemeris,
        "metadata",
        lambda self: (_ for _ in ()).throw(EphemerisUnavailableError("native binding unavailable")),
    )
    response = TestClient(app).get("/api/astrology/config")
    assert response.status_code == 200
    assert response.json()["engine_available"] is False
    assert "path" not in str(response.json()).lower()


def test_calculation_request_rejects_invalid_coordinates_before_engine():
    response = TestClient(app).post("/api/astrology/calculate", json={
        "birth_date": "2000-01-01", "birth_time": "12:00:00",
        "timezone": "Asia/Kolkata", "city": "Test", "country": "India",
        "latitude": 91, "longitude": 0,
    })
    assert response.status_code == 422


def test_native_binding_contract_when_available():
    try:
        import swisseph as swe
    except Exception as exc:
        pytest.skip(f"native Swiss Ephemeris binding unavailable: {exc}")
    assert str(swe.version).startswith("2.10")
    assert all(hasattr(swe, name) for name in (
        "calc_ut", "houses_ex", "julday", "set_sid_mode", "set_ephe_path", "get_ayanamsa_ut"
    ))
