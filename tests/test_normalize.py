from __future__ import annotations

import pytest

from phonodist import InvalidIPAError, parse_ipa


def test_zero_width_joiner_is_ignored() -> None:
    parsed = parse_ipa("t\u200ds", language="de-DE")
    assert "\u200d" not in parsed.normalized
    assert any(item.reason == "unicode_format_character" for item in parsed.diagnostics)


def test_stress_is_ignored_by_default() -> None:
    left = parse_ipa("ˈluft", language="de-DE")
    right = parse_ipa("luft", language="de-DE")
    assert left.segments == right.segments


def test_diagnostic_offsets_reference_normalized_working_input() -> None:
    parsed = parse_ipa(" / a b /", language=None)
    assert parsed.original == " / a b /"
    assert parsed.normalized == "ab"
    assert parsed.diagnostics[0].offset == 1


def test_diagnostic_offset_excludes_outer_delimiters() -> None:
    parsed = parse_ipa("/ˈa/", language=None)
    assert parsed.diagnostics[0].offset == 0
    assert parsed.diagnostics[0].text == "ˈ"


def test_nfc_and_nfd_diacritics_are_equivalent() -> None:
    nfc = parse_ipa("ã", language=None)
    nfd = parse_ipa("a\u0303", language=None)
    assert nfc.normalized == nfd.normalized
    assert nfc.segments == nfd.segments == ("ã",)


def test_supported_ipa_diacritics_are_single_segments() -> None:
    for value in ("n̩", "ã", "aː", "tʰ"):
        assert len(parse_ipa(value).segments) == 1


@pytest.mark.parametrize("value", ["ˈ", "\u200d", "[ˈ]"])
def test_malformed_ipa_raises_invalid_ipa_error(value: str) -> None:
    with pytest.raises(InvalidIPAError, match="no parseable IPA"):
        parse_ipa(value, language=None)


def test_empty_ipa_remains_defined() -> None:
    assert parse_ipa("", language=None).normalized == ""
