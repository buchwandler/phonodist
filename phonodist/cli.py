from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from collections.abc import Sequence

from .api import pronunciation_distance


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phonodist",
        description="Language-aware IPA pronunciation distance.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare = subparsers.add_parser("compare", help="compare two IPA pronunciations")
    compare.add_argument("language", help="language/profile tag, e.g. de-DE")
    compare.add_argument("source", help="source IPA")
    compare.add_argument("target", help="target IPA")
    compare.add_argument(
        "--keep-stress",
        action="store_true",
        help="retain IPA stress marks instead of broad stress-insensitive comparison",
    )
    compare.add_argument("--explain", action="store_true", help="print alignment operations")
    compare.add_argument("--json", action="store_true", help="emit JSON")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "compare":
        parser.error(f"unsupported command: {args.command}")

    result = pronunciation_distance(
        args.source,
        args.target,
        language=args.language,
        ignore_stress=not args.keep_stress,
    )

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0

    print(f"distance: {result.distance:.6f}")
    print(f"raw_cost: {result.raw_cost:.6f}")
    print(f"metric: {result.metric}/{result.metric_version}")
    if result.language is not None:
        print(f"profile: {result.language}/{result.profile_version}")

    if result.source.diagnostics or result.target.diagnostics:
        print("normalization:")
        for side, parsed in (("source", result.source), ("target", result.target)):
            for diagnostic in parsed.diagnostics:
                print(f"  {side}: {diagnostic.codepoint} {diagnostic.action} ({diagnostic.reason})")

    if args.explain:
        print("alignment:")
        for operation in result.operations:
            source = " ".join(operation.source) or "∅"
            target = " ".join(operation.target) or "∅"
            print(
                f"  {source:<12} -> {target:<12} "
                f"cost={operation.cost:.4f} "
                f"{operation.kind}: {operation.reason}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
