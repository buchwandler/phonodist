from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict
from typing import cast

from . import __version__
from .api import compare_pronunciations, pronunciation_distance
from .errors import PhonodistError
from .model import DistanceResult, PronunciationComparison, StressOperation


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phonodist",
        description="Language-aware IPA pronunciation distance.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare = subparsers.add_parser("compare", help="compare two IPA pronunciations")
    compare.add_argument("language", help="language/profile tag, e.g. de-DE")
    compare.add_argument("source", help="source IPA")
    compare.add_argument("target", help="target IPA")
    compare.add_argument("--explain", action="store_true", help="print alignment operations")
    compare.add_argument("--json", action="store_true", help="emit JSON")

    diff = subparsers.add_parser("diff", help="explain structural IPA differences")
    diff.add_argument("source", help="source IPA")
    diff.add_argument("target", help="target IPA")
    diff.add_argument("--language", default=None, help="optional language/profile tag, e.g. de-DE")
    diff.add_argument("--explain", action="store_true", help="print comparison operations")
    diff.add_argument("--json", action="store_true", help="emit JSON")

    return parser


def _print_alignment(result: DistanceResult | PronunciationComparison) -> None:
    operations = (
        result.segmental.operations
        if isinstance(result, PronunciationComparison)
        else result.operations
    )
    print("alignment:")
    for operation in operations:
        source = " ".join(operation.source) or "∅"
        target = " ".join(operation.target) or "∅"
        print(
            f"  {source:<12} -> {target:<12} "
            f"cost={operation.cost:.4f} {operation.kind}: {operation.reason}"
        )


def _print_stress_operation(operation: StressOperation) -> None:
    source = f"{operation.source.kind}@{operation.source.anchor}" if operation.source else "none"
    target = f"{operation.target.kind}@{operation.target.anchor}" if operation.target else "none"
    if operation.kind == "insert":
        print(f"  insert {target}")
    elif operation.kind == "delete":
        print(f"  delete {source}")
    else:
        print(f"  replace {source} -> {target}")


def _print_diff(comparison: PronunciationComparison, *, explain: bool) -> None:
    print(f"classification: {comparison.classification}")
    print(f"raw_equal: {str(comparison.raw_equal).lower()}")
    print(f"canonical_equal: {str(comparison.canonical_equal).lower()}")
    print(f"segment_relation: {comparison.segment_relation}")
    print(f"segment_equal: {str(comparison.segment_equal).lower()}")
    print(f"stress_equal: {str(comparison.stress_equal).lower()}")
    print(f"segment_distance: {comparison.segmental.distance:.6f}")
    print("stress:")
    source = (
        ", ".join(f"{event.kind}@{event.anchor}" for event in comparison.source.stress) or "none"
    )
    target = (
        ", ".join(f"{event.kind}@{event.anchor}" for event in comparison.target.stress) or "none"
    )
    print(f"  source: {source}")
    print(f"  target: {target}")

    if explain:
        print("stress operations:")
        if comparison.stress_operations:
            for operation in comparison.stress_operations:
                _print_stress_operation(operation)
        else:
            print("  none")
        if comparison.segmental.operations:
            _print_alignment(comparison)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    result: DistanceResult | PronunciationComparison
    try:
        if args.command == "compare":
            result = pronunciation_distance(
                args.source,
                args.target,
                language=args.language,
                explain=args.explain,
            )
        else:
            result = compare_pronunciations(
                args.source,
                args.target,
                language=args.language,
                explain=args.explain,
            )
    except PhonodistError as error:
        parser.exit(2, f"phonodist: {error}\n")
    except NotImplementedError as error:
        parser.exit(2, f"phonodist: {error}\n")

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0

    if args.command == "diff":
        _print_diff(cast(PronunciationComparison, result), explain=args.explain)
        return 0
    distance_result = cast(DistanceResult, result)

    print(f"distance: {distance_result.distance:.6f}")
    print(f"raw_cost: {distance_result.raw_cost:.6f}")
    print(f"metric: {distance_result.metric}/{distance_result.metric_version}")
    print(
        f"backend: {distance_result.backend}/{distance_result.backend_version} "
        f"({distance_result.feature_set})"
    )
    if distance_result.language is not None:
        print(f"profile: {distance_result.language}/{distance_result.profile_version}")

    if distance_result.source.diagnostics or distance_result.target.diagnostics:
        print("normalization:")
        for side, parsed in (
            ("source", distance_result.source),
            ("target", distance_result.target),
        ):
            for diagnostic in parsed.diagnostics:
                print(f"  {side}: {diagnostic.codepoint} {diagnostic.action} ({diagnostic.reason})")

    if args.explain:
        _print_alignment(distance_result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
