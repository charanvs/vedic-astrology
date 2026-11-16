from fastapi import APIRouter, Query
from app.schemas.geocoding import GeocodingSuggestion
from app.services.geocoding import search as search_cities

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.get("/search", response_model=list[GeocodingSuggestion])
def search(q: str = Query(min_length=2, max_length=150), limit: int = Query(10, ge=1, le=25)):
    return [
        GeocodingSuggestion(name=city.name, state=city.state or None, country=city.country, country_code=city.country_code, latitude=city.latitude, longitude=city.longitude, timezone=city.timezone)
        for city in search_cities(q, limit)
    ]
