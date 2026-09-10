from __future__ import annotations

from phonodist import parse_ipa, pronunciation_distance


def test_syllabic_nasal_equivalence_is_low_cost_and_symmetric() -> None:
    forward = pronunciation_distance("n̩", "ən", language="de-DE", explain=True)
    reverse = pronunciation_distance("ən", "n̩", language="de-DE", explain=True)

    assert forward.distance == reverse.distance
    assert forward.raw_cost == 0.10
    assert any(op.kind == "sequence_equivalence" for op in forward.operations)


def test_german_affricate_notation_is_equivalent() -> None:
    assert parse_ipa("t͜s", language="de-DE").segments == ("t͡s",)
    for left, right in (("ts", "t͡s"), ("pf", "p͡f"), ("tʃ", "t͡ʃ")):
        result = pronunciation_distance(left, right, language="de-DE", explain=True)
        assert result.distance == 0.0
        assert any(op.kind == "sequence_equivalence" for op in result.operations)


def test_luftwaffenstuetzpunkt_regression() -> None:
    lexicon = "ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt"
    espeak = "lˈʊftvˌafənʃtˌʏt\u200dspʊŋkt"

    result = pronunciation_distance(lexicon, espeak, language="de-DE", explain=True)

    assert result.distance < 0.10
    assert any(op.kind == "sequence_equivalence" for op in result.operations)
    assert any(
        diagnostic.reason == "unicode_format_character" for diagnostic in result.target.diagnostics
    )
