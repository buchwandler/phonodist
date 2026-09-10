from __future__ import annotations

from importlib.resources import files
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

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


def get_profile(language: str) -> LanguageProfile:
    language = normalize_language_tag(language)
    if language not in available_profiles():
        raise UnknownLanguageProfileError(f"no bundled profile for {language!r}")

    path = files("phonodist").joinpath("data", "profiles", f"{language}.toml")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    try:
        aliases = tuple(
            AliasRule(
                input=str(item["input"]),
                canonical=str(item["canonical"]),
                reason=str(item["reason"]),
            )
            for item in raw.get("aliases", [])
        )
        equivalences = tuple(
            SequenceEquivalence(
                left=_as_string_tuple(item["left"], "sequence_equivalences.left"),
                right=_as_string_tuple(item["right"], "sequence_equivalences.right"),
                cost=float(item["cost"]),
                reason=str(item["reason"]),
            )
            for item in raw.get("sequence_equivalences", [])
        )

        for rule in equivalences:
            if not (0.0 <= rule.cost <= 1.0):
                raise ProfileValidationError(f"sequence equivalence cost must be in [0, 1]: {rule}")

        return LanguageProfile(
            id=str(raw["id"]),
            version=str(raw["version"]),
            name=str(raw["name"]),
            default_ignore_stress=bool(raw.get("default_ignore_stress", True)),
            inventory=_as_string_tuple(raw.get("inventory", []), "inventory"),
            aliases=aliases,
            sequence_equivalences=equivalences,
            sources=_as_string_tuple(raw.get("sources", []), "sources"),
        )
    except KeyError as exc:
        raise ProfileValidationError(f"missing required profile field: {exc}") from exc
