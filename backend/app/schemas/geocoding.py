from pydantic import BaseModel


class GeocodingSuggestion(BaseModel):
    name: str
    state: str | None
    country: str
    country_code: str
    latitude: str
    longitude: str
    timezone: str
