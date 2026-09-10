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


def test_german_affricate_alias_is_canonicalized() -> None:
    tied = parse_ipa("t͡s", language="de-DE")
    untied = parse_ipa("ts", language="de-DE")
    assert tied.segments == untied.segments == ("t͡s",)
