from fastapi.testclient import TestClient
from zoneinfo import ZoneInfo
from app.main import create_app

client = TestClient(create_app())


def test_search_requires_minimum_query_length():
 assert client.get("/api/geocoding/search", params={"q": "a"}).status_code == 422


def test_search_returns_known_city_with_coordinates_and_valid_timezone():
 response = client.get("/api/geocoding/search", params={"q": "chandigarh"})
 assert response.status_code == 200
 results = response.json()
 assert results
 match = next(item for item in results if item["name"] == "Chandigarh")
 assert match["country"] == "India" and match["country_code"] == "IN"
 assert -90 <= float(match["latitude"]) <= 90 and -180 <= float(match["longitude"]) <= 180
 assert ZoneInfo(match["timezone"]) is not None


def test_search_is_case_insensitive_and_matches_state_or_country():
 lower = client.get("/api/geocoding/search", params={"q": "mumbai"}).json()
 upper = client.get("/api/geocoding/search", params={"q": "MUMBAI"}).json()
 assert lower and lower == upper
 by_country = client.get("/api/geocoding/search", params={"q": "andorra"}).json()
 assert any(item["country"] == "Andorra" for item in by_country)


def test_search_respects_limit_and_returns_empty_list_for_no_match():
 limited = client.get("/api/geocoding/search", params={"q": "san", "limit": 3}).json()
 assert len(limited) <= 3
 assert client.get("/api/geocoding/search", params={"q": "zzzznotarealplace"}).json() == []


def test_search_requires_no_authentication():
 assert client.get("/api/geocoding/search", params={"q": "paris"}).status_code == 200
