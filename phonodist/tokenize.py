from __future__ import annotations

import unicodedata

from ._symbols import STRESS_MARKERS
from .model import LanguageProfile

_TIE_BAR = "\u0361"

# Common IPA modifier letters/marks that are encoded as spacing characters rather
# than Unicode combining marks. This is deliberately small in the MVP.
_POSTFIX_MODIFIERS = frozenset(
    {
        "ː",
        "ˑ",
        "ʰ",
        "ʱ",
        "ʲ",
        "ʷ",
        "ˠ",
        "ˤ",
        "ⁿ",
        "ˡ",
        "ᵊ",
        "ᵐ",
        "ᵑ",
    }
)

_STRESS = frozenset({"ˈ", "ˌ"})


def apply_aliases(value: str, profile: LanguageProfile | None) -> str:
    if profile is None:
        return value

    result = value
    for rule in sorted(profile.aliases, key=lambda item: len(item.input), reverse=True):
        result = result.replace(rule.input, rule.canonical)
    return result


def ipa_units(value: str) -> tuple[str, ...]:
    """Split normalized IPA into approximate segment units.

    PanPhon remains the authority for whether a resulting segment has a valid
    feature representation. The tokenizer's job is to avoid codepoint-level edits.
    """
    units: list[str] = []
    i = 0

    while i < len(value):
        char = value[i]

        if char in STRESS_MARKERS:
            units.append(char)
            i += 1
            continue

        if unicodedata.combining(char):
            if units:
                units[-1] += char
            else:
                units.append(char)
            i += 1
            continue

        unit = char
        i += 1

        # Attach ordinary combining marks/modifiers to the base.
        while i < len(value):
            next_char = value[i]
            if next_char == _TIE_BAR:
                break
            if unicodedata.combining(next_char) or next_char in _POSTFIX_MODIFIERS:
                unit += next_char
                i += 1
                continue
            break

        # Handle a tied affricate/co-articulated segment as one unit.
        if i < len(value) and value[i] == _TIE_BAR:
            unit += value[i]
            i += 1
            if i < len(value):
                unit += value[i]
                i += 1
                while i < len(value):
                    next_char = value[i]
                    if unicodedata.combining(next_char) or next_char in _POSTFIX_MODIFIERS:
                        unit += next_char
                        i += 1
                        continue
                    break

        units.append(unicodedata.normalize("NFC", unit))

    return tuple(units)
