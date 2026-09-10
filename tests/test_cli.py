from __future__ import annotations

import json

import pytest

from phonodist.cli import main


def test_cli_json_and_explain(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["compare", "de-DE", "n̩", "ən", "--json", "--explain"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["backend"] == "panphon"
    assert output["operations"]


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
