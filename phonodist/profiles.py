from __future__ import annotations

from functools import cache
from importlib.resources import files
from typing import Any

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

from .errors import ProfileValidationError, UnknownLanguageProfileError
from .model import AliasRule, LanguageProfile, SequenceEquivalence

_ALIASES = {
    "de": "de-DE",
    "de-de": "de-DE",
}


def normalize_language_tag(language: str) -> str:
    raw = language.strip().replace("_", "-")
    mapped = _ALIASES.get(raw.lower())
    if mapped is not None:
        return mapped

    parts = raw.split("-")
    if len(parts) == 1:
        return parts[0].lower()
    return "-".join([parts[0].lower(), parts[1].upper(), *parts[2:]])


def available_profiles() -> tuple[str, ...]:
    return ("de-DE",)


def _as_string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProfileValidationError(f"{field} must be a list of strings")
    return tuple(value)


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProfileValidationError(f"{field} must be a non-empty string")
    return value


def _profile_from_raw(raw: Any, language: str) -> LanguageProfile:
    if not isinstance(raw, dict):
        raise ProfileValidationError("profile data must be a table")
    if raw.get("schema_version") != 1:
        raise ProfileValidationError("schema_version must be 1")
    profile_id = _required_string(raw.get("id"), "id")
    if profile_id != language:
        raise ProfileValidationError(
            f"profile id {profile_id!r} does not match requested language {language!r}"
        )
    profile_version = _required_string(raw.get("version"), "version")
    name = _required_string(raw.get("name"), "name")

    aliases_value = raw.get("aliases", [])
    if not isinstance(aliases_value, list):
        raise ProfileValidationError("aliases must be a list")
    aliases: list[AliasRule] = []
    alias_inputs: set[str] = set()
    for item in aliases_value:
        if not isinstance(item, dict):
            raise ProfileValidationError("aliases must contain tables")
        alias_input = _required_string(item.get("input"), "aliases.input")
        canonical = _required_string(item.get("canonical"), "aliases.canonical")
        reason = _required_string(item.get("reason"), "aliases.reason")
        if alias_input in alias_inputs:
            raise ProfileValidationError(f"duplicate alias input: {alias_input!r}")
        alias_inputs.add(alias_input)
        aliases.append(AliasRule(input=alias_input, canonical=canonical, reason=reason))

    equivalences_value = raw.get("sequence_equivalences", [])
    if not isinstance(equivalences_value, list):
        raise ProfileValidationError("sequence_equivalences must be a list")
    equivalences: list[SequenceEquivalence] = []
    for item in equivalences_value:
        if not isinstance(item, dict):
            raise ProfileValidationError("sequence_equivalences must contain tables")
        left = _as_string_tuple(item.get("left"), "sequence_equivalences.left")
        right = _as_string_tuple(item.get("right"), "sequence_equivalences.right")
        if not left and not right:
            raise ProfileValidationError("sequence equivalence cannot have two empty sides")
        cost_value = item.get("cost")
        if not isinstance(cost_value, (int, float)) or isinstance(cost_value, bool):
            raise ProfileValidationError("sequence equivalence cost must be a number")
        cost = float(cost_value)
        if not 0.0 <= cost <= 1.0:
            raise ProfileValidationError(f"sequence equivalence cost must be in [0, 1]: {cost}")
        reason = _required_string(item.get("reason"), "sequence_equivalences.reason")
        equivalences.append(SequenceEquivalence(left=left, right=right, cost=cost, reason=reason))

    default_ignore_stress = raw.get("default_ignore_stress", True)
    if not isinstance(default_ignore_stress, bool):
        raise ProfileValidationError("default_ignore_stress must be a boolean")

    return LanguageProfile(
        id=profile_id,
        version=profile_version,
        name=name,
        default_ignore_stress=default_ignore_stress,
        inventory=_as_string_tuple(raw.get("inventory", []), "inventory"),
        aliases=tuple(aliases),
        sequence_equivalences=tuple(equivalences),
        sources=_as_string_tuple(raw.get("sources", []), "sources"),
    )


def get_profile(language: str) -> LanguageProfile:
    return _load_profile(normalize_language_tag(language))


@cache
def _load_profile(language: str) -> LanguageProfile:
    if language not in available_profiles():
        raise UnknownLanguageProfileError(f"no bundled profile for {language!r}")

    path = files("phonodist").joinpath("data").joinpath("profiles").joinpath(f"{language}.toml")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    return _profile_from_raw(raw, language)
