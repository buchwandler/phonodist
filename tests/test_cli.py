from __future__ import annotations

import json

import pytest

from phonodist.cli import main


def test_cli_json_and_explain(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["compare", "de-DE", "n̩", "ən", "--json", "--explain"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["backend"] == "panphon"
    assert output["operations"]


def test_cli_readme_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main(
            [
                "compare",
                "de-DE",
                "ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt",
                "lˈʊftvˌafənʃtˌʏtspʊŋkt",
                "--explain",
            ]
        )
        == 0
    )
    assert "distance:" in capsys.readouterr().out


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--version"])

    assert error.value.code == 0
    assert capsys.readouterr().out.strip()


def test_cli_unknown_profile_is_concise(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["compare", "en-US", "p", "b"])

    assert error.value.code == 2
    assert capsys.readouterr().err.startswith("phonodist: no bundled profile")


def test_cli_rejects_removed_keep_stress_flag() -> None:
    with pytest.raises(SystemExit) as error:
        main(["compare", "de-DE", "ˈa", "a", "--keep-stress"])

    assert error.value.code == 2


def test_diff_cli_reports_stress_only(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["diff", "wɪ\u200dɹ", "wˈɪ\u200dɹ"]) == 0

    output = capsys.readouterr().out
    assert "classification: stress_only" in output
    assert "segment_distance: 0.000000" in output


def test_diff_cli_json_reports_nested_segmental_result(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["diff", "wɪ\u200dɹ", "wˈɪ\u200dɹ", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["classification"] == "stress_only"
    assert output["segmental"]["distance"] == 0.0


def test_diff_cli_accepts_optional_profile(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["diff", "--language", "de-DE", "t͡s", "ts"]) == 0

    assert "classification: phonetic_equivalent" in capsys.readouterr().out
