from decimal import Decimal
from enum import Enum


class DashaYearConvention(str, Enum):
    TROPICAL_365_25 = "365.25_day"
    SAVANA_360 = "360_day_savana"

    @property
    def days(self) -> Decimal:
        return Decimal("365.25") if self is self.TROPICAL_365_25 else Decimal("360")

    @property
    def label(self) -> str:
        return "365.25-day Dasha year" if self is self.TROPICAL_365_25 else "360-day Savana year"


class DetailLevel(str, Enum):
    MAHADASHA = "mahadasha"
    ANTARDASHA = "antardasha"
    PRATYANTARDASHA = "pratyantardasha"


SECONDS_PER_DAY = Decimal(86_400)
DEFAULT_YEAR_CONVENTION = DashaYearConvention.TROPICAL_365_25
DEFAULT_DETAIL_LEVEL = DetailLevel.ANTARDASHA
