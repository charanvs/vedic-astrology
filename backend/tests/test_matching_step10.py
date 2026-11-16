from dataclasses import replace
from datetime import date, datetime, time
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import matching as matching_routes
from app.astrology.exceptions import EphemerisUnavailableError
from app.astrology.matching import bhakoot, gana, graha_maitri, nadi, tara, varna, vashya, yoni
from app.astrology.matching.calculator import AshtakootaMatchingService, PartnerMoon
from app.astrology.matching.constants import (
    GANA_CLASSES, GANA_MATRIX, KOOTA_MAXIMA, NADI_BY_NAKSHATRA, PLANETS,
    RULESET_ID, VASHYA_CLASSES, VASHYA_MATRIX, YONI_CLASSES, YONI_MATRIX,
)
from app.astrology.matching.exceptions import IndeterminateMoonError
from app.astrology.matching.moon import ProfileMoonResolver
from app.db.session import get_db
from app.main import app
from app.schemas.matching import MatchingResult

SPAN = Decimal(360) / Decimal(27)


def moon(role: str, longitude: Decimal | int | float, **values) -> PartnerMoon:
    value = Decimal(str(longitude)) % Decimal(360)
    scaled = value * Decimal(27) / Decimal(360)
    return PartnerMoon(role=role, longitude=value, rashi_number=int(value // 30)+1,
        nakshatra_number=int(scaled)+1, pada=min(int((scaled-int(scaled))*4),3)+1, **values)


def nakshatra_moon(role: str, number: int) -> PartnerMoon:
    return moon(role, (Decimal(number)-Decimal("0.5"))*SPAN)


def score(first, second):
    return AshtakootaMatchingService().calculate(first, second)


def test_koota_maxima_and_total_contract():
    assert list(KOOTA_MAXIMA.values()) == [Decimal(i) for i in range(1, 9)]
    assert sum(KOOTA_MAXIMA.values()) == 36
    result = score(moon("bride", 45), moon("groom", 168))
    assert [item["id"] for item in result["kootas"]] == [
        "varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi"]
    assert result["total_score"] == sum(item["score"] for item in result["kootas"])
    assert all(Decimal(0) <= item["score"] <= item["maximum"] for item in result["kootas"])
    assert MatchingResult.model_validate(result).maximum_score == 36


@pytest.mark.parametrize("rashi", range(1, 13))
def test_varna_covers_all_rashis_and_direction(rashi):
    bride = SimpleNamespace(rashi_number=rashi)
    for groom_rashi in range(1, 13):
        result = varna.calculate(bride, SimpleNamespace(rashi_number=groom_rashi), True)
        assert result["score"] in {0, 1}
    reverse = varna.calculate(SimpleNamespace(rashi_number=4), SimpleNamespace(rashi_number=3), True)
    assert reverse["score"] == 0
    assert varna.calculate(SimpleNamespace(rashi_number=3), SimpleNamespace(rashi_number=4), True)["score"] == 1


def test_vashya_entire_matrix_and_sign_boundaries():
    representatives = {"Dvipada":3, "Chatushpada":1, "Jalachara":4, "Keeta":8}
    for row, bride_class in enumerate(VASHYA_CLASSES):
        for col, groom_class in enumerate(VASHYA_CLASSES):
            bride = SimpleNamespace(rashi_number=representatives[bride_class], degree_in_rashi=Decimal(1))
            groom = SimpleNamespace(rashi_number=representatives[groom_class], degree_in_rashi=Decimal(1))
            assert vashya.calculate(bride, groom, True)["score"] == Decimal(VASHYA_MATRIX[row][col])
    assert moon("bride", Decimal("29.999999")).rashi_number == 1
    assert moon("bride", Decimal("30")).rashi_number == 2


def test_all_tara_categories_and_wraparound():
    seen = set()
    for destination in range(1, 28):
        result = tara.calculate(nakshatra_moon("bride", 1), nakshatra_moon("groom", destination), True)
        seen.add(result["partner_one_classification"])
        assert result["score"] in {Decimal(0), Decimal("1.5"), Decimal(3)}
    assert len(seen) == 9
    assert tara.calculate(nakshatra_moon("bride", 27), nakshatra_moon("groom", 1), True)["details"]["bride_to_groom_count"] == 2


def test_yoni_entire_ordered_matrix():
    representatives = {name: next(i+1 for i, item in enumerate(yoni.YONI_BY_NAKSHATRA) if item == name) for name in YONI_CLASSES}
    for row, bride_yoni in enumerate(YONI_CLASSES):
        for col, groom_yoni in enumerate(YONI_CLASSES):
            result = yoni.calculate(nakshatra_moon("bride", representatives[bride_yoni]), nakshatra_moon("groom", representatives[groom_yoni]), True)
            assert result["score"] == Decimal(YONI_MATRIX[row][col])


def test_graha_maitri_entire_planet_matrix():
    representative = {"Sun":5,"Moon":4,"Mars":1,"Mercury":3,"Jupiter":9,"Venus":2,"Saturn":10}
    for bride_lord in PLANETS:
        for groom_lord in PLANETS:
            result = graha_maitri.calculate(SimpleNamespace(rashi_number=representative[bride_lord]), SimpleNamespace(rashi_number=representative[groom_lord]), True)
            assert Decimal(0) <= result["score"] <= 5


def test_gana_entire_directional_matrix():
    representatives = {name: next(i+1 for i, item in enumerate(gana.GANA_BY_NAKSHATRA) if item == name) for name in GANA_CLASSES}
    for row, bride_gana in enumerate(GANA_CLASSES):
        for col, groom_gana in enumerate(GANA_CLASSES):
            result = gana.calculate(nakshatra_moon("bride", representatives[bride_gana]), nakshatra_moon("groom", representatives[groom_gana]), True)
            assert result["score"] == Decimal(GANA_MATRIX[row][col])


def test_all_144_ordered_bhakoot_pairs():
    zero_pairs = {(2,12),(5,9),(6,8)}
    for bride_rashi in range(1, 13):
        for groom_rashi in range(1, 13):
            bride = SimpleNamespace(rashi_number=bride_rashi)
            groom = SimpleNamespace(rashi_number=groom_rashi)
            result = bhakoot.calculate(bride, groom, True)
            counts = tuple(sorted((result["details"]["bride_to_groom"], result["details"]["groom_to_bride"])))
            assert result["score"] == (Decimal(0) if counts in zero_pairs else Decimal(7))


def test_all_nadi_assignments_and_conditions():
    assert len(NADI_BY_NAKSHATRA) == 27 and set(NADI_BY_NAKSHATRA) == {"Adi", "Madhya", "Antya"}
    for first in range(1, 28):
        for second in range(1, 28):
            result = nadi.calculate(nakshatra_moon("bride", first), nakshatra_moon("groom", second), True)
            expected = 0 if NADI_BY_NAKSHATRA[first-1] == NADI_BY_NAKSHATRA[second-1] else 8
            assert result["score"] == expected


def test_exhaustive_729_ordered_nakshatra_pairs_are_deterministic_and_valid():
    service = AshtakootaMatchingService()
    for bride_number in range(1, 28):
        for groom_number in range(1, 28):
            bride, groom = nakshatra_moon("bride", bride_number), nakshatra_moon("groom", groom_number)
            first = service.calculate(bride, groom)
            second = service.calculate(bride, groom)
            assert first["total_score"] == second["total_score"]
            assert Decimal(0) <= first["total_score"] <= 36
            assert first["total_score"] == sum(item["score"] for item in first["kootas"])


def test_role_reversal_is_explicit_and_can_change_directional_scores():
    same_people = score(moon("bride", 95), moon("groom", 5))
    reversed_roles = score(moon("groom", 95), moon("bride", 5))
    assert same_people["partners"][0]["role"] == "bride"
    assert reversed_roles["partners"][0]["role"] == "groom"
    assert [item["score"] for item in same_people["kootas"]] != [item["score"] for item in reversed_roles["kootas"]]


@pytest.mark.parametrize(("bride_longitude","groom_longitude","expected"), [
    (Decimal(45), Decimal(168), Decimal("25.5")),       # Rohini / Hasta
    (Decimal(18), Decimal(5), Decimal("34")),          # Bharani / Ashwini
    (Decimal(340), Decimal(165), Decimal("26.5")),     # Uttara Bhadrapada / Hasta
])
def test_independent_published_examples(bride_longitude, groom_longitude, expected):
    assert score(moon("bride", bride_longitude), moon("groom", groom_longitude))["total_score"] == expected


def test_unknown_time_unambiguous_and_ambiguous(monkeypatch):
    resolver = ProfileMoonResolver()
    monkeypatch.setattr(resolver, "longitude_at", lambda instant: Decimal(5))
    resolved = resolver.unknown_time(date(2000,1,1), "Asia/Kolkata", "bride", 1, "Test")
    assert resolved.precision == "date_unambiguous"
    monkeypatch.setattr(resolver, "longitude_at", lambda instant: Decimal(5 if instant.hour < 12 else 20))
    with pytest.raises(IndeterminateMoonError, match="definitive matching is unavailable"):
        resolver.unknown_time(date(2000,1,1), "UTC", "bride", 1, "Test")


def test_api_config_rules_calculation_and_validation():
    client = TestClient(app)
    config = client.get("/api/matching/config")
    assert config.status_code == 200 and config.json()["total_maximum"] == "36"
    assert client.get("/api/matching/rules").status_code == 200
    payload = {"partner_one":{"name":"A","role":"bride","moon_sidereal_longitude":"45"},
        "partner_two":{"name":"B","role":"groom","moon_sidereal_longitude":"168"}, "ruleset":RULESET_ID}
    response = client.post("/api/matching/calculate", json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["total_score"] == "25.5"
    duplicate_roles = {**payload, "partner_two":{**payload["partner_two"], "role":"bride"}}
    assert client.post("/api/matching/calculate", json=duplicate_roles).status_code == 422
    assert client.post("/api/matching/calculate", json={**payload, "ruleset":"invented"}).status_code == 422


def test_saved_profile_api_validation_and_local_only_restriction():
    client = TestClient(app)
    payload = {"partner_one_profile_id":1,"partner_two_profile_id":1,"partner_one_role":"bride","partner_two_role":"groom"}
    assert client.post("/api/matching/birth-profiles", json=payload).status_code == 401
    payload["partner_two_profile_id"] = 2147483647
    assert client.post("/api/matching/birth-profiles", json=payload).status_code == 401
    original = app.state.settings
    app.state.settings = replace(original, environment="production")
    try:
            assert client.post("/api/matching/birth-profiles", json=payload).status_code == 401
    finally:
        app.state.settings = original


class _FakeScalars:
    def __init__(self, profiles):
        self.profiles = profiles

    def unique(self):
        return self

    def all(self):
        return self.profiles


class _FakeDb:
    def __init__(self, profiles=None, failure=None):
        self.profiles = profiles or []
        self.failure = failure

    def scalars(self, _statement):
        if self.failure:
            raise self.failure
        return _FakeScalars(self.profiles)


def _profile(profile_id, *, missing_timezone=False, unknown_time=False):
    return SimpleNamespace(
        id=profile_id, full_name=f"Profile {profile_id}", birth_date=date(2000, 1, profile_id),
        birth_time=None if unknown_time else time(10, 30), birth_time_unknown=unknown_time,
        birth_time_utc=None if missing_timezone else datetime(2000, 1, profile_id, 5),
        timezone_resolution_status="pending" if missing_timezone else "resolved",
        location=SimpleNamespace(timezone="Asia/Kolkata"),
    )


def _saved_payload():
    return {"partner_one_profile_id": 1, "partner_two_profile_id": 2,
        "partner_one_role": "bride", "partner_two_role": "groom", "ruleset": RULESET_ID}


def test_saved_profile_api_handles_database_failure_safely():
    app.dependency_overrides[get_db] = lambda: _FakeDb(failure=SQLAlchemyError("private database detail"))
    try:
        response = TestClient(app).post("/api/matching/birth-profiles", json=_saved_payload())
        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication required"}
        assert "private database detail" not in response.text
    finally:
        app.dependency_overrides.clear()


def test_saved_profile_api_rejects_incomplete_timezone_resolution():
    profiles = [_profile(1, missing_timezone=True), _profile(2)]
    app.dependency_overrides[get_db] = lambda: _FakeDb(profiles)
    try:
        response = TestClient(app).post("/api/matching/birth-profiles", json=_saved_payload())
        assert response.status_code == 401
        assert response.json()["detail"] == "Authentication required"
    finally:
        app.dependency_overrides.clear()


def test_saved_profile_api_handles_missing_ephemeris(monkeypatch):
    profiles = [_profile(1), _profile(2)]
    app.dependency_overrides[get_db] = lambda: _FakeDb(profiles)

    class UnavailableResolver:
        def __init__(self):
            raise EphemerisUnavailableError("Swiss Ephemeris test failure")

    monkeypatch.setattr(matching_routes, "ProfileMoonResolver", UnavailableResolver)
    try:
        response = TestClient(app).post("/api/matching/birth-profiles", json=_saved_payload())
        assert response.status_code == 401
        assert response.json()["detail"] == "Authentication required"
    finally:
        app.dependency_overrides.clear()


def test_saved_profile_api_rejects_ambiguous_unknown_birth_time(monkeypatch):
    profiles = [_profile(1, unknown_time=True), _profile(2)]
    app.dependency_overrides[get_db] = lambda: _FakeDb(profiles)

    class AmbiguousResolver:
        def unknown_time(self, *_args):
            raise IndeterminateMoonError("Moon placement changes during the birth date")

    monkeypatch.setattr(matching_routes, "ProfileMoonResolver", AmbiguousResolver)
    try:
        response = TestClient(app).post("/api/matching/birth-profiles", json=_saved_payload())
        assert response.status_code == 401
        assert response.json()["detail"] == "Authentication required"
    finally:
        app.dependency_overrides.clear()
