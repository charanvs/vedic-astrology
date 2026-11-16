class DashaError(ValueError):
    """A Vimshottari Dasha input or reference instant is invalid."""


class DashaReferenceOutOfRange(DashaError):
    """The requested instant is outside the generated 120-year cycle."""
