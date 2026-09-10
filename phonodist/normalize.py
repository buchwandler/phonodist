from __future__ import annotations

import unicodedata

from .model import ParseDiagnostic

_PRIMARY_STRESS = "ˈ"
_SECONDARY_STRESS = "ˌ"
_TIE_BAR_BELOW = "\u035c"
_TIE_BAR_ABOVE = "\u0361"


def _diagnostic(
    *,
    offset: int,
    text: str,
    action: str,
    reason: str,
) -> ParseDiagnostic:
    codepoint = " ".join(f"U+{ord(char):04X}" for char in text)
    category = ",".join(unicodedata.category(char) for char in text)
    return ParseDiagnostic(
        offset=offset,
        text=text,
        codepoint=codepoint,
        category=category,
        action=action,  # type: ignore[arg-type]
        reason=reason,
    )


def normalize_ipa(
    value: str,
    *,
    ignore_stress: bool = True,
) -> tuple[str, tuple[ParseDiagnostic, ...]]:
    """Normalize IPA representation without applying language-specific rules."""
    original = value
    value = unicodedata.normalize("NFC", value.strip())
    diagnostics: list[ParseDiagnostic] = []

    if len(value) >= 2 and (
        (value.startswith("/") and value.endswith("/"))
        or (value.startswith("[") and value.endswith("]"))
    ):
        value = value[1:-1].strip()

    output: list[str] = []

    for offset, char in enumerate(value):
        category = unicodedata.category(char)

        if char.isspace():
            diagnostics.append(
                _diagnostic(
                    offset=offset,
                    text=char,
                    action="ignored",
                    reason="ipa_spacing",
                )
            )
            continue

        if category == "Cf":
            diagnostics.append(
                _diagnostic(
                    offset=offset,
                    text=char,
                    action="ignored",
                    reason="unicode_format_character",
                )
            )
            continue

        if ignore_stress and char in {_PRIMARY_STRESS, _SECONDARY_STRESS}:
            diagnostics.append(
                _diagnostic(
                    offset=offset,
                    text=char,
                    action="ignored",
                    reason="stress_ignored",
                )
            )
            continue

        if char == _TIE_BAR_BELOW:
            diagnostics.append(
                _diagnostic(
                    offset=offset,
                    text=char,
                    action="normalized",
                    reason="tie_bar_variant",
                )
            )
            output.append(_TIE_BAR_ABOVE)
            continue

        output.append(char)

    normalized = unicodedata.normalize("NFC", "".join(output))
    if not normalized and original.strip():
        return normalized, tuple(diagnostics)
    return normalized, tuple(diagnostics)
