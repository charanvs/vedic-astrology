from datetime import UTC, date, datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

import pytest
from pypdf import PdfReader

from app.astrology.transits import TransitCalculator
from app.reports.calculations import FORECAST_SPAN, collect_kundli
from app.reports.generator import KundliReportService
from app.reports.interpretation import GOCHARA_BODIES, HOUSES, TRANSIT_PLANETS, build_forecast, readings
from app.reports.schemas import KundliReportRequest
from tests.test_report_interpretation import has_script
from tests.test_reports_step12 import synthetic_profile

IST = ZoneInfo("Asia/Kolkata")
REFERENCE = datetime(2026, 11, 15, tzinfo=UTC)


def ingress_dates(planet, start, end):
    return [(segment.sign, segment.start_utc.astimezone(IST).date()) for segment in TransitCalculator().segments(planet, start, end)]


def test_saturn_ingress_matches_published_lahiri_dates():
    # Published Lahiri ingresses: Kumbha 17 Jan 2023, Meena 29 Mar 2025.
    dates = ingress_dates("saturn", datetime(2024, 1, 1, tzinfo=UTC), datetime(2026, 1, 1, tzinfo=UTC))
    assert (11, date(2023, 1, 17)) in dates and (12, date(2025, 3, 29)) in dates


def test_jupiter_ingresses_including_retrograde_reentry_match_published_dates():
    # Published Lahiri ingresses: Mithuna 14 May 2025, Karka 18 Oct 2025, back to Mithuna 5 Dec 2025, Karka 2 Jun 2026.
    dates = ingress_dates("jupiter", datetime(2025, 6, 1, tzinfo=UTC), datetime(2026, 7, 1, tzinfo=UTC))
    for expected in [(3, date(2025, 5, 14)), (4, date(2025, 10, 18)), (3, date(2025, 12, 5)), (4, date(2026, 6, 2))]:
        assert expected in dates


def test_mean_rahu_ingress_matches_published_lahiri_dates():
    # Published Lahiri ingresses of mean Rahu: Mesha 12 Apr 2022, Meena 30 Oct 2023, Kumbha 18 May 2025.
    dates = ingress_dates("rahu", datetime(2023, 1, 1, tzinfo=UTC), datetime(2025, 12, 1, tzinfo=UTC))
    for expected in [(1, date(2022, 4, 12)), (12, date(2023, 10, 30)), (11, date(2025, 5, 18))]:
        assert expected in dates


@pytest.mark.parametrize("planet", TRANSIT_PLANETS)
def test_segments_are_contiguous_adjacent_signs_covering_the_window(planet):
    start, end = REFERENCE, REFERENCE + FORECAST_SPAN
    segments = TransitCalculator().segments(planet, start, end)
    assert segments[0].start_utc <= start and segments[-1].end_utc >= end
    for previous, following in zip(segments, segments[1:]):
        assert previous.end_utc == following.start_utc
        assert (following.sign - previous.sign) % 12 in (1, 11)


def forecast(language="en"):
    profile = synthetic_profile()
    values = collect_kundli(profile, "summary", {"forecast"}, "365.25_day", REFERENCE)
    return values, build_forecast(values["d1"], values["dasha"], values["transits"], values["forecast_window"], profile.location.timezone, language)


def test_dasha_periods_cover_the_window_without_gaps_and_mark_one_current():
    values, result = forecast()
    periods = result["periods"]
    assert periods[0]["start"] <= REFERENCE.date() and periods[-1]["end"] >= (REFERENCE + FORECAST_SPAN).date()
    for previous, following in zip(periods, periods[1:]):
        assert previous["end"] == following["start"]
    assert sum(period["current"] for period in periods) == 1
    houses = {planet["identifier"]: str(planet["house"]) for planet in values["d1"]["planets"]}
    current = next(child for maha in values["dasha"]["mahadashas"] for child in maha["children"] if child["start_utc"] <= REFERENCE < child["end_utc"])
    reading = next(period for period in periods if period["current"])
    assert reading["text"].startswith(readings("en")["antardasha"][current["planet_identifier"]])
    assert readings("en")["house_focus"][houses[current["planet_identifier"]]] in reading["text"]


def test_transit_readings_are_counted_from_the_natal_moon():
    values, result = forecast()
    moon_sign = next(p for p in values["d1"]["planets"] if p["identifier"] == "moon")["rashi"]["number"]
    gochara = readings("en")["gochara"]
    for item in result["transits"]:
        assert item["house"] == (item["sign"] - moon_sign) % 12 + 1
        if item["planet"] == "rahu":
            assert (item["ketu_sign"] - item["sign"]) % 12 == 6 and (item["ketu_house"] - item["house"]) % 12 == 6
            assert item["text"] == f"{gochara['rahu'][str(item['house'])]} {gochara['ketu'][str(item['ketu_house'])]}"
        else:
            assert item["text"] == gochara[item["planet"]][str(item["house"])]
    for planet in TRANSIT_PLANETS:
        assert sum(item["current"] for item in result["transits"] if item["planet"] == planet) == 1
    assert [item["start"] for item in result["transits"]] == sorted(item["start"] for item in result["transits"])


def test_forecast_catalogs_are_complete_and_in_the_right_script():
    for language in ("en", "hi", "pa"):
        values = readings(language)
        assert set(values["antardasha"]) == set(values["planet_names"])
        for planet in GOCHARA_BODIES:
            assert set(values["gochara"][planet]) == set(HOUSES)
    texts = lambda lang: [*readings(lang)["antardasha"].values(), *readings(lang)["house_focus"].values(), *readings(lang)["sign_names"].values(),
        *(t for p in GOCHARA_BODIES for t in readings(lang)["gochara"][p].values())]
    assert all(has_script(text, 0x0900, 0x097F) for text in texts("hi"))
    assert all(has_script(text, 0x0A00, 0x0A7F) and not has_script(text, 0x0900, 0x097F) for text in texts("pa"))


@pytest.mark.parametrize("language", ["en", "hi", "pa"])
def test_forecast_section_renders_in_every_language(language):
    request = KundliReportRequest(profile_id=1, language=language, sections=["forecast"], reference_datetime=REFERENCE)
    pdf, _ = KundliReportService().kundli_for_profile(synthetic_profile(), request)
    pages = PdfReader(BytesIO(pdf)).pages
    assert pdf.startswith(b"%PDF-") and len(pages) >= 2
    if language == "en":
        text = " ".join(page.extract_text() for page in pages)
        assert "Period-wise Forecast" in text and "Antardasha" in text and "from the Moon" in text and "Ketu in" in text
