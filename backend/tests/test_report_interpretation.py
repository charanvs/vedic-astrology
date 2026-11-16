import json
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace

import pytest
from pypdf import PdfReader

from app.astrology.matching.calculator import AshtakootaMatchingService
from app.astrology.matching.constants import RULESET_ID
from app.astrology.matching.moon import ProfileMoonResolver
from app.reports import generator, interpretation
from app.reports.calculations import collect_kundli
from app.reports.generator import KundliReportService
from app.reports.interpretation import (HOUSES, KOOTA_STATES, KOOTAS, PLANETS, REQUIRED_KEYS, build_house_readings,
    build_interpretation, build_matching_interpretation, koota_state, readings, score_band)
from app.reports.localization import MissingTranslationError
from app.reports.schemas import KundliReportRequest, MatchingReportRequest
from tests.test_reports_step12 import synthetic_profile

REFERENCE = datetime(2026, 11, 15, tzinfo=UTC)


SHARED_DANDAS = {"।", "॥"}


def has_script(text: str, start: int, end: int) -> bool:
    return any(start <= ord(char) <= end for char in text if char not in SHARED_DANDAS)


@pytest.mark.parametrize("language", ["en", "hi", "pa"])
def test_every_language_has_every_reading(language):
    values = readings(language)
    for group, keys in REQUIRED_KEYS.items():
        assert set(values[group]) == keys
    assert set(values["planet_house"]) == set(PLANETS)
    for planet in PLANETS:
        assert set(values["planet_house"][planet]) == set(HOUSES)


def all_texts(language: str) -> list[str]:
    values = readings(language)
    texts = [entry["text"] for group in REQUIRED_KEYS for entry in values[group].values()]
    texts += [text for houses in values["planet_house"].values() for text in houses.values()]
    texts += list(values["planet_names"].values()) + list(values["house_ordinals"].values())
    texts += [entry[field] for entry in values["matching_kootas"].values() for field in ("title", *KOOTA_STATES)]
    return texts


def test_hindi_and_punjabi_readings_use_their_own_scripts():
    for text in all_texts("hi"):
        assert has_script(text, 0x0900, 0x097F)
    for text in all_texts("pa"):
        assert has_script(text, 0x0A00, 0x0A7F) and not has_script(text, 0x0900, 0x097F)


def test_missing_reading_fails_closed(tmp_path, monkeypatch):
    incomplete = json.loads((interpretation.INTERPRETATION_ROOT / "en.json").read_text(encoding="utf-8"))
    del incomplete["nakshatra"]["27"]
    (tmp_path / "en.json").write_text(json.dumps(incomplete), encoding="utf-8")
    monkeypatch.setattr(interpretation, "INTERPRETATION_ROOT", tmp_path)
    readings.cache_clear()
    try:
        with pytest.raises(MissingTranslationError, match="nakshatra: 27"):
            readings("en")
    finally:
        readings.cache_clear()


def test_missing_planet_house_reading_fails_closed(tmp_path, monkeypatch):
    incomplete = json.loads((interpretation.INTERPRETATION_ROOT / "pa.json").read_text(encoding="utf-8"))
    del incomplete["planet_house"]["saturn"]["7"]
    (tmp_path / "pa.json").write_text(json.dumps(incomplete, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(interpretation, "INTERPRETATION_ROOT", tmp_path)
    readings.cache_clear()
    try:
        with pytest.raises(MissingTranslationError, match="planet_house.saturn.7"):
            readings("pa")
    finally:
        readings.cache_clear()


@pytest.mark.parametrize("language", ["en", "hi", "pa"])
def test_house_readings_follow_each_planets_calculated_house(language):
    d1 = collect_kundli(synthetic_profile(), "summary", set(), "365.25_day", None)["d1"]
    items = build_house_readings(d1, language)
    houses = {planet["identifier"]: planet["house"] for planet in d1["planets"]}
    assert [item["planet"] for item in items] == list(PLANETS)
    for item in items:
        assert item["house"] == houses[item["planet"]]
        assert item["text"] == readings(language)["planet_house"][item["planet"]][str(item["house"])]
        assert readings(language)["planet_names"][item["planet"]] in item["title"]
        assert readings(language)["house_ordinals"][str(item["house"])] in item["title"]


def test_english_house_titles_read_naturally():
    d1 = collect_kundli(synthetic_profile(), "summary", set(), "365.25_day", None)["d1"]
    sun = build_house_readings(d1, "en")[0]
    assert sun["title"] == f"Sun in the {readings('en')['house_ordinals'][str(sun['house'])]} house"


def test_readings_follow_the_calculated_chart():
    values = collect_kundli(synthetic_profile(), "summary", {"interpretation"}, "365.25_day", REFERENCE)
    items = build_interpretation(values["d1"], values["dasha"], "en")
    assert [item["label_key"] for item in items] == ["lagna", "moon_rashi", "birth_nakshatra", "current_mahadasha"]
    moon = next(p for p in values["d1"]["planets"] if p["identifier"] == "moon")
    assert items[0]["title"] == readings("en")["lagna"][str(values["d1"]["lagna"]["rashi"]["number"])]["title"]
    assert items[1]["title"] == readings("en")["moon_rashi"][str(moon["rashi"]["number"])]["title"]
    assert items[2]["title"] == readings("en")["nakshatra"][str(moon["nakshatra"]["number"])]["title"]
    mahadasha = values["dasha"]["current"]["mahadasha"]
    assert items[3]["title"] == readings("en")["mahadasha"][mahadasha["planet_identifier"]]["title"]
    assert items[3]["period"] == (mahadasha["start_local"].date(), mahadasha["end_local"].date())


@pytest.mark.parametrize("language", ["en", "hi", "pa"])
def test_interpretation_section_renders_in_every_language(language):
    request = KundliReportRequest(profile_id=1, language=language, sections=["d1_chart", "interpretation"], reference_datetime=REFERENCE)
    pdf, _ = KundliReportService().kundli_for_profile(synthetic_profile(), request)
    assert pdf.startswith(b"%PDF-") and len(PdfReader(BytesIO(pdf)).pages) >= 3


def test_english_pdf_contains_readings_and_drops_positions_only_notice():
    request = KundliReportRequest(profile_id=1, language="en", sections=["d1_chart", "interpretation"], reference_datetime=REFERENCE)
    pdf, _ = KundliReportService().kundli_for_profile(synthetic_profile(), request)
    text = " ".join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
    assert "Traditional Interpretation" in text and "Lagna" in text and "Mahadasha" in text
    assert "Planets in the Houses" in text and "Ketu in the" in text
    assert "no predictive interpretation" not in text


@pytest.mark.parametrize("total,band", [("36", "excellent"), ("33", "excellent"), ("32.5", "good"), ("25", "good"), ("24.5", "average"), ("18", "average"), ("17.5", "low"), ("0", "low")])
def test_matching_score_bands_use_traditional_thresholds(total, band):
    assert score_band(Decimal(total)) == band


def test_koota_state_distinguishes_full_partial_and_none():
    assert koota_state(Decimal("8"), Decimal("8")) == "full"
    assert koota_state(Decimal("0.5"), Decimal("2")) == "partial"
    assert koota_state(Decimal("0"), Decimal("7")) == "none"


def real_matching_result():
    resolver = ProfileMoonResolver()
    bride = resolver.exact(datetime(2000, 1, 15, 5, 0, tzinfo=UTC), "bride", 1, "Bride")
    groom = resolver.exact(datetime(1998, 6, 3, 9, 30, tzinfo=UTC), "groom", 2, "Groom")
    return AshtakootaMatchingService().calculate(bride, groom, RULESET_ID)


@pytest.mark.parametrize("language", ["en", "hi", "pa"])
def test_matching_readings_follow_the_calculated_scores(language):
    result = real_matching_result()
    reading = build_matching_interpretation(result, language)
    assert reading["band"] == readings(language)["matching_bands"][score_band(result["total_score"])]
    by_id = {koota["id"]: koota for koota in result["kootas"]}
    assert [item["id"] for item in reading["kootas"]] == list(KOOTAS)
    for item in reading["kootas"]:
        koota = by_id[item["id"]]
        assert (item["score"], item["maximum"]) == (koota["score"], koota["maximum"])
        assert item["text"] == readings(language)["matching_kootas"][item["id"]][koota_state(koota["score"], koota["maximum"])]


def test_nadi_reading_never_presents_a_dosha_as_health_evidence():
    for language, phrase in (("en", "not medical, genetic or health evidence"), ("hi", "चिकित्सा"), ("pa", "ਡਾਕਟਰੀ")):
        assert phrase in readings(language)["matching_kootas"]["nadi"]["none"]


def test_missing_matching_reading_fails_closed(tmp_path, monkeypatch):
    incomplete = json.loads((interpretation.INTERPRETATION_ROOT / "hi.json").read_text(encoding="utf-8"))
    del incomplete["matching_kootas"]["gana"]["partial"]
    (tmp_path / "hi.json").write_text(json.dumps(incomplete, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(interpretation, "INTERPRETATION_ROOT", tmp_path)
    readings.cache_clear()
    try:
        with pytest.raises(MissingTranslationError, match="matching_kootas.gana.partial"):
            readings("hi")
    finally:
        readings.cache_clear()


@pytest.mark.parametrize("language", ["en", "hi", "pa"])
def test_matching_pdf_includes_interpretation_in_every_language(language, monkeypatch):
    result = real_matching_result()
    first, second = SimpleNamespace(id=1, full_name="Bride Synthetic"), SimpleNamespace(id=2, full_name="Groom Synthetic")
    monkeypatch.setattr(generator, "collect_matching", lambda *args: (first, second, result))
    payload = MatchingReportRequest(partner_one_profile_id=1, partner_two_profile_id=2, partner_one_role="bride", partner_two_role="groom", language=language)
    pdf, _ = KundliReportService().matching(None, payload)
    pages = PdfReader(BytesIO(pdf)).pages
    assert pdf.startswith(b"%PDF-") and len(pages) >= 3
    if language == "en":
        text = " ".join(page.extract_text() for page in pages)
        assert "Traditional Interpretation" in text and "Overall assessment" in text and "sole basis" in text


def test_positions_only_notice_remains_without_interpretation():
    request = KundliReportRequest(profile_id=1, language="en", sections=["d1_chart"])
    pdf, _ = KundliReportService().kundli_for_profile(synthetic_profile(), request)
    text = " ".join(page.extract_text() for page in PdfReader(BytesIO(pdf)).pages)
    assert "no predictive interpretation" in text and "Traditional Interpretation" not in text
