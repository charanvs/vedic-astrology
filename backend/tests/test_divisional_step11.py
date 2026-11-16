from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.astrology.divisional.boundaries import decimal_degrees
from app.astrology.divisional.calculator import build_divisional_chart
from app.astrology.divisional.dashamsha import dashamsha_position
from app.astrology.divisional.navamsha import navamsha_position
from app.main import app


def test_all_108_navamsha_segments_against_continuous_count():
    width = Decimal(30) / Decimal(9)
    for segment in range(108):
        longitude = Decimal(segment) * width + width / 2
        result = navamsha_position(longitude)
        assert result["sign_number"] == segment % 12 + 1
        assert result["division_number"] == segment % 9 + 1
        assert result["degree"] == pytest.approx(Decimal(15), abs=Decimal("1e-24"))


def test_all_120_dashamsha_segments_against_parashari_table():
    for sign in range(12):
        start = sign if sign % 2 == 0 else (sign + 8) % 12
        for division in range(10):
            result = dashamsha_position(Decimal(sign * 30 + division * 3) + Decimal("1.5"))
            assert result["sign_number"] == (start + division) % 12 + 1
            assert result["division_number"] == division + 1
            assert result["degree"] == Decimal(15)


@pytest.mark.parametrize(("longitude", "sign", "division"), [
    (Decimal(180 + 19), 12, 6),  # 19 degrees Libra -> Pisces
    (Decimal(30 + 5), 11, 2),    # 5 degrees Taurus -> Aquarius
])
def test_documented_navamsha_examples(longitude, sign, division):
    result = navamsha_position(longitude)
    assert (result["sign_number"], result["division_number"]) == (sign, division)


@pytest.mark.parametrize(("longitude", "sign", "division"), [
    (Decimal(7), 3, 3),          # 7 degrees Aries -> Gemini
    (Decimal(31), 10, 1),        # 1 degree Taurus -> Capricorn
    (Decimal(150 + 25), 10, 9),  # 25 degrees Virgo -> Capricorn
])
def test_documented_dashamsha_examples(longitude, sign, division):
    result = dashamsha_position(longitude)
    assert (result["sign_number"], result["division_number"]) == (sign, division)


def test_exact_boundaries_are_half_open_and_wrap_is_deterministic():
    before = navamsha_position(Decimal(30) / Decimal(9) - Decimal("1e-20"))
    exact = navamsha_position(Decimal(30) / Decimal(9))
    assert before["division_number"] == 1 and exact["division_number"] == 2
    assert dashamsha_position(Decimal("2.999999999"))["division_number"] == 1
    assert dashamsha_position(Decimal(3))["division_number"] == 2
    assert decimal_degrees(Decimal(360)) == 0
    assert navamsha_position(Decimal(360))["sign_number"] == 1
    with pytest.raises(ValueError, match="finite"):
        navamsha_position(float("nan"))


def _d1_fixture():
    rashi = lambda number, within: {"number": number, "name": "", "english_name": "", "hindi_name": "", "longitude_within": within}
    planet = {"identifier": "sun", "english_name": "Sun", "sanskrit_name": "Surya", "hindi_name": "",
              "longitude": 0.0, "longitude_formatted": "0", "latitude": 0.0, "longitude_speed": 1.0,
              "motion": "direct", "retrograde": False, "rashi": rashi(1, 0),
              "nakshatra": {"number": 1, "name": "Ashwini", "pada": 1, "longitude_within": 0, "lord": "Ketu"},
              "house": 1, "calculation_flags": 0, "ephemeris_source": "test", "convention": "test"}
    return {"birth_datetime": {}, "location": {}, "settings": {"zodiac": "sidereal", "ayanamsa": "Lahiri",
            "ayanamsa_mode": "SIDM_LAHIRI", "planetary_reference": "geocentric", "node_convention": "mean lunar node",
            "house_system": "whole-sign", "calendar": "Gregorian", "ephemeris_source": "test", "stationary_threshold": 0.0001},
            "julian_day_ut": 1, "julian_day_calendar": "Gregorian", "ayanamsa": {},
            "lagna": {"longitude": 7.0}, "planets": [planet], "engine": {}, "warnings": []}


def test_chart_rebuilds_whole_sign_houses_and_marks_d9_vargottama():
    chart = build_divisional_chart(_d1_fixture(), "D9")
    assert len(chart["houses"]) == 12
    assert chart["houses"][0]["rashi_number"] == chart["lagna"]["rashi"]["number"]
    assert chart["planets"][0]["vargottama"] is True
    assert chart["planets"][0]["house"] == 11
    assert any("boundary" in warning for warning in chart["warnings"])


def test_divisional_config_and_calculation_api():
    client = TestClient(app)
    config = client.get("/api/divisional/config")
    assert config.status_code == 200
    assert [item["chart_type"] for item in config.json()["supported_charts"]] == ["D9", "D10"]
    response = client.post("/api/divisional/calculate", json={
        "chart_type": "D9", "birth_date": "2000-01-15", "birth_time": "10:30:00",
        "timezone": "Asia/Kolkata", "city": "Chandigarh", "state": "Chandigarh",
        "country": "India", "latitude": 30.7333, "longitude": 76.7794,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["chart_type"] == "D9" and len(body["planets"]) == 9 and len(body["houses"]) == 12
    assert response.json()["calculation"]["interval_semantics"].startswith("half-open")


def test_invalid_chart_type_is_rejected_before_calculation():
    response = TestClient(app).post("/api/divisional/calculate", json={
        "chart_type": "D7", "birth_date": "2000-01-15", "birth_time": "10:30:00",
        "timezone": "Asia/Kolkata", "city": "Test", "country": "India", "latitude": 0, "longitude": 0,
    })
    assert response.status_code == 422
