from __future__ import annotations

from phonodist import parse_ipa


def test_zero_width_joiner_is_ignored() -> None:
    parsed = parse_ipa("t\u200ds", language="de-DE")
    assert "\u200d" not in parsed.normalized
    assert any(item.reason == "unicode_format_character" for item in parsed.diagnostics)


def test_stress_is_ignored_by_default() -> None:
    left = parse_ipa("ˈluft", language="de-DE")
    right = parse_ipa("luft", language="de-DE")
    assert left.segments == right.segments


def test_nfc_and_nfd_diacritics_are_equivalent() -> None:
    nfc = parse_ipa("ã", language=None)
    nfd = parse_ipa("a\u0303", language=None)
    assert nfc.normalized == nfd.normalized
    assert nfc.segments == nfd.segments == ("ã",)


def test_supported_ipa_diacritics_are_single_segments() -> None:
    for value in ("n̩", "ã", "aː", "tʰ"):
        assert len(parse_ipa(value).segments) == 1
