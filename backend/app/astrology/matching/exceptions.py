class MatchingError(ValueError):
    """Base error safe for conversion to an API response."""


class UnsupportedRulesetError(MatchingError):
    pass


class IndeterminateMoonError(MatchingError):
    pass
