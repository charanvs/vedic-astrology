from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.astrology.dasha import DashaInput, DashaYearConvention, DetailLevel, VimshottariDashaService
from app.astrology.dasha.balance import calculate_nakshatra_balance
from app.astrology.dasha.constants import DASHA_SEQUENCE, DASHA_YEARS, TOTAL_DASHA_YEARS, sequence_from
from app.astrology.dasha.exceptions import DashaReferenceOutOfRange
from app.astrology.dasha.timeline import DashaPeriod, find_active, partition_period
from app.main import app
from app.schemas.dasha import DashaTimelineResponse


def synthetic_input(
    convention=DashaYearConvention.TROPICAL_365_25,
    detail=DetailLevel.PRATYANTARDASHA,
    reference=None,
    timezone="Asia/Kolkata",
):
    birth = datetime(2000, 1, 15, 5, tzinfo=UTC)
    return DashaInput(
        birth_utc=birth, timezone=timezone, latitude=30.7333, longitude=76.7794,
        city="Chandigarh", state="Chandigarh", country="India", full_name="Synthetic",
        year_convention=convention, reference_utc=reference or birth + timedelta(days=1),
        detail_level=detail,
    )


def test_sequence_durations_and_total():
    assert DASHA_SEQUENCE == (
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
    )
    assert DASHA_YEARS == {
        "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
        "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
    }
    assert TOTAL_DASHA_YEARS == 120
    assert sequence_from("Saturn") == (
        "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter"
    )


@pytest.mark.parametrize("index,lord", list(enumerate(DASHA_SEQUENCE)))
def test_all_nakshatra_starting_lords(index, lord):
    longitude = Decimal(str(index * (360 / 27) + 1))
    balance = calculate_nakshatra_balance(longitude)
    assert balance.lord == lord
    assert 0 < balance.elapsed_fraction < 1
    assert 0 < balance.remaining_fraction < 1


@pytest.mark.parametrize("fraction,expected", [
    (Decimal(0), Decimal(1)),
    (Decimal("0.5"), Decimal("0.5")),
    (Decimal("0.999999999"), Decimal("0.000000001")),
])
def test_nakshatra_balance_fractions(fraction, expected):
    span = Decimal(40) / Decimal(3)
    result = calculate_nakshatra_balance(span * fraction)
    assert abs(result.remaining_fraction - expected) < Decimal("1e-25")


def test_exact_boundary_and_near_360_normalization():
    span = Decimal(40) / Decimal(3)
    boundary = calculate_nakshatra_balance(span)
    assert boundary.nakshatra_number == 2 and boundary.lord == "Venus"
    assert boundary.elapsed_fraction == 0
    near_end = calculate_nakshatra_balance(Decimal("359.999999999"))
    assert near_end.nakshatra_number == 27 and near_end.lord == "Mercury"
    assert calculate_nakshatra_balance(Decimal(360)).nakshatra_number == 1


def test_birth_balance_and_nine_mahadashas_cover_120_years():
    result = VimshottariDashaService().calculate(synthetic_input(), moon_longitude=5.0)
    periods = result["mahadashas"]
    birth = synthetic_input().birth_utc
    assert len(periods) == 9
    assert periods[0]["start_utc"] < birth < periods[0]["end_utc"]
    assert periods[0]["active_at_birth"]
    assert result["balance"]["elapsed_years"] > 0
    assert result["balance"]["remaining_years"] > 0
    assert (periods[-1]["end_utc"] - periods[0]["start_utc"]).total_seconds() == 120 * 365.25 * 86400
    for left, right in zip(periods, periods[1:]):
        assert left["end_utc"] == right["start_utc"]


def test_all_antardashas_and_pratyantardashas_exactly_partition_parents():
    result = VimshottariDashaService().calculate(synthetic_input(), moon_longitude=0)
    for maha in result["mahadashas"]:
        assert len(maha["children"]) == 9
        assert maha["children"][0]["lord"] == maha["lord"]
        assert maha["children"][0]["start_utc"] == maha["start_utc"]
        assert maha["children"][-1]["end_utc"] == maha["end_utc"]
        for left, right in zip(maha["children"], maha["children"][1:]):
            assert left["end_utc"] == right["start_utc"]
        for antar in maha["children"]:
            assert len(antar["children"]) == 9
            assert antar["children"][0]["lord"] == antar["lord"]
            assert antar["children"][0]["start_utc"] == antar["start_utc"]
            assert antar["children"][-1]["end_utc"] == antar["end_utc"]
            for left, right in zip(antar["children"], antar["children"][1:]):
                assert left["end_utc"] == right["start_utc"]


def test_theoretical_antardasha_is_not_restarted_at_birth():
    birth = synthetic_input().birth_utc
    result = VimshottariDashaService().calculate(synthetic_input(reference=birth), moon_longitude=6.5)
    active = result["current"]["antardasha"]
    first_maha = result["mahadashas"][0]
    assert first_maha["start_utc"] < birth
    assert active["start_utc"] <= birth < active["end_utc"]
    assert active["start_utc"] != birth


def test_half_open_transition_selects_new_period():
    service = VimshottariDashaService()
    initial = service.calculate(synthetic_input(detail=DetailLevel.MAHADASHA), moon_longitude=0)
    transition = initial["mahadashas"][0]["end_utc"]
    at_boundary = service.calculate(
        synthetic_input(detail=DetailLevel.MAHADASHA, reference=transition), moon_longitude=0
    )
    assert at_boundary["current"]["mahadasha"]["lord"] == "Venus"


def test_year_conventions_recalculate_boundaries_and_leap_spans():
    service = VimshottariDashaService()
    standard = service.calculate(synthetic_input(), moon_longitude=0)
    savana = service.calculate(
        synthetic_input(DashaYearConvention.SAVANA_360), moon_longitude=0
    )
    standard_end = standard["mahadashas"][0]["end_utc"]
    savana_end = savana["mahadashas"][0]["end_utc"]
    assert (standard_end - synthetic_input().birth_utc).total_seconds() == 7 * 365.25 * 86400
    assert (savana_end - synthetic_input().birth_utc).total_seconds() == 7 * 360 * 86400
    assert standard_end != savana_end


def test_local_rendering_uses_historical_timezone_offset():
    birth = datetime(1945, 8, 14, 16, tzinfo=UTC)
    data = DashaInput(
        birth, "America/New_York", 40.7128, -74.006, "New York", "New York", "USA",
        reference_utc=birth + timedelta(days=1), detail_level=DetailLevel.MAHADASHA,
    )
    result = VimshottariDashaService().calculate(data, moon_longitude=0)
    assert result["profile"]["birth_local"].utcoffset() is not None
    assert result["profile"]["birth_local"].astimezone(UTC) == birth


def test_reference_outside_cycle_is_rejected():
    with pytest.raises(DashaReferenceOutOfRange):
        VimshottariDashaService().calculate(
            synthetic_input(reference=datetime(2200, 1, 1, tzinfo=UTC)), moon_longitude=0
        )


def test_partition_helper_proportions_and_active_lookup():
    start = datetime(2000, 1, 1, tzinfo=UTC)
    parent = DashaPeriod("mahadasha", "Saturn", start, start + timedelta(days=1900), Decimal(19))
    children = partition_period(parent, "antardasha")
    assert [item.lord for item in children] == list(sequence_from("Saturn"))
    expected = Decimal(19) * Decimal(19) / Decimal(120)
    assert abs(children[0].duration_years - expected) < Decimal("1e-27")
    assert find_active(children, children[1].start_utc) is children[1]


def test_response_schema_validates_full_hierarchy():
    result = VimshottariDashaService().calculate(synthetic_input(), moon_longitude=0)
    validated = DashaTimelineResponse.model_validate(result)
    assert len(validated.mahadashas) == 9
    assert validated.settings["interval_semantics"] == "[start, end)"


def test_dasha_config_and_valid_calculation_api():
    client = TestClient(app)
    config = client.get("/api/dasha/config")
    assert config.status_code == 200
    assert config.json()["planetary_sequence"] == list(DASHA_SEQUENCE)
    response = client.post("/api/dasha/calculate", json={
        "birth_date": "2000-01-15", "birth_time": "10:30:00",
        "timezone": "Asia/Kolkata", "city": "Chandigarh", "country": "India",
        "latitude": 30.7333, "longitude": 76.7794,
        "reference_datetime": "2026-11-13T00:00:00Z", "detail_level": "antardasha",
    })
    assert response.status_code == 200, response.text
    assert len(response.json()["mahadashas"]) == 9


@pytest.mark.parametrize("payload", [
    {"year_convention": "calendar_year"},
    {"reference_datetime": "2026-01-01T00:00:00"},
    {"moon_sidereal_longitude": 361},
])
def test_api_rejects_invalid_settings_and_unsupported_moon_override(payload):
    base = {
        "birth_date": "2000-01-15", "birth_time": "10:30:00", "timezone": "Asia/Kolkata",
        "city": "Chandigarh", "country": "India", "latitude": 30.7333, "longitude": 76.7794,
        "reference_datetime": "2026-11-13T00:00:00Z",
    }
    response = TestClient(app).post("/api/dasha/calculate", json={**base, **payload})
    assert response.status_code == 422


def test_independent_manual_balance_examples():
    half_ashwini = calculate_nakshatra_balance(Decimal(20) / Decimal(3))
    assert half_ashwini.lord == "Ketu"
    assert abs(half_ashwini.remaining_years - Decimal("3.5")) < Decimal("1e-25")

    # Sanatan Veda example: Punarvasu has 564 of 800 arcminutes remaining.
    punarvasu = calculate_nakshatra_balance(Decimal(80) + Decimal(236) / Decimal(60))
    assert punarvasu.lord == "Jupiter"
    assert abs(punarvasu.remaining_years - Decimal("11.28")) < Decimal("1e-25")

    # Mathematical Astrology example: Rohini has 193 of 800 arcminutes remaining.
    rohini = calculate_nakshatra_balance(Decimal(40) + Decimal(607) / Decimal(60))
    assert rohini.lord == "Moon"
    assert abs(rohini.remaining_years - Decimal("2.4125")) < Decimal("1e-25")


def test_independent_new_delhi_reference_dates_and_current_hierarchy():
    data = DashaInput(
        birth_utc=datetime(2001, 1, 19, 8, 35, tzinfo=UTC), timezone="Asia/Kolkata",
        latitude=28.6139, longitude=77.209, city="New Delhi", state="Delhi", country="India",
        reference_utc=datetime(2026, 11, 13, tzinfo=UTC),
        detail_level=DetailLevel.PRATYANTARDASHA,
    )
    result = VimshottariDashaService().calculate(data)
    assert result["birth_moon"]["nakshatra"] == "Anuradha"
    assert result["balance"]["starting_lord"] == "Saturn"
    assert result["mahadashas"][0]["start_local"].date().isoformat() == "1993-05-27"
    assert result["mahadashas"][1]["start_local"].date().isoformat() == "2012-05-27"
    assert result["mahadashas"][1]["end_local"].date().isoformat() == "2029-05-27"
    assert result["current"]["mahadasha"]["lord"] == "Mercury"
    assert result["current"]["antardasha"]["lord"] == "Saturn"
    assert result["current"]["pratyantardasha"]["lord"] == "Saturn"
    assert result["current"]["pratyantardasha"]["end_local"].date().isoformat() == "2027-02-19"


def test_invalid_profile_and_local_only_restriction():
    client = TestClient(app)
    assert client.get("/api/dasha/birth-profiles/2147483647").status_code == 401
    original = app.state.settings
    app.state.settings = replace(original, environment="production")
    try:
        response = client.get("/api/dasha/birth-profiles/1")
        assert response.status_code == 401
    finally:
        app.state.settings = original
