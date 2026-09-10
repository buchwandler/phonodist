from __future__ import annotations

from phonodist import pronunciation_distance


def test_syllabic_nasal_equivalence_is_low_cost_and_symmetric() -> None:
    forward = pronunciation_distance("n̩", "ən", language="de-DE")
    reverse = pronunciation_distance("ən", "n̩", language="de-DE")

    assert forward.distance == reverse.distance
    assert forward.raw_cost == 0.10
    assert any(op.kind == "sequence_equivalence" for op in forward.operations)


def test_luftwaffenstuetzpunkt_regression() -> None:
    lexicon = "ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt"
    espeak = "lˈʊftvˌafənʃtˌʏt\u200dspʊŋkt"

    result = pronunciation_distance(lexicon, espeak, language="de-DE")

    assert result.distance < 0.10
    assert any(op.kind == "sequence_equivalence" for op in result.operations)
    assert any(
        diagnostic.reason == "unicode_format_character" for diagnostic in result.target.diagnostics
    )
