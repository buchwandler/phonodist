from __future__ import annotations


class PhonodistError(Exception):
    """Base class for phonodist errors."""


class InvalidIPAError(PhonodistError):
    """Raised when an IPA value cannot be normalized or parsed."""


class UnknownSegmentError(PhonodistError):
    """Raised when the feature backend cannot represent an IPA segment."""


class UnknownLanguageProfileError(PhonodistError):
    """Raised when a requested language profile is unavailable."""


class ProfileValidationError(PhonodistError):
    """Raised when bundled or supplied profile data is invalid."""
