class AstrologyError(Exception):
    """Base error safe for conversion to an API response."""


class EphemerisUnavailableError(AstrologyError):
    """The configured native engine or requested ephemeris source is unavailable."""


class UnsupportedDateError(AstrologyError):
    """The date is outside the documented application range."""


class CalculationError(AstrologyError):
    """Swiss Ephemeris could not complete a requested calculation."""


class SunEventUnavailableError(AstrologyError):
    """A required sunrise or sunset does not occur on the requested civil date."""


class TransitionSearchError(AstrologyError):
    """A bounded Panchang transition search could not converge safely."""


class SunEventUnavailableError(AstrologyError):
    """A required sunrise or sunset does not occur on the requested civil date."""


class TransitionSearchError(AstrologyError):
    """A bounded Panchang transition search could not converge safely."""
