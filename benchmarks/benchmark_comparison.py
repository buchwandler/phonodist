from __future__ import annotations

import argparse
from time import perf_counter

from phonodist import compare_pronunciations, get_profile, pronunciation_distance

CASES = (
    ("exact", "p", "p", None),
    ("stress", "wɪ\u200dɹ", "wˈɪ\u200dɹ", None),
    ("german", "t͡s", "ts", "de-DE"),
    ("segmental", "p", "b", None),
)


def _measure_comparisons(count: int) -> float:
    start = perf_counter()
    for _ in range(count):
        for _, source, target, language in CASES:
            compare_pronunciations(source, target, language=language)
    return perf_counter() - start


def _measure_distances(count: int) -> float:
    start = perf_counter()
    for _ in range(count):
        for _, source, target, language in CASES:
            pronunciation_distance(source, target, language=language)
    return perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure structural comparison throughput.")
    parser.add_argument("--count", type=int, default=1000)
    args = parser.parse_args()

    get_profile("de-DE")
    comparisons = args.count * len(CASES)
    comparison_seconds = _measure_comparisons(args.count)
    distance_seconds = _measure_distances(args.count)

    print(f"comparison_cases={len(CASES)}")
    print(f"comparison_calls={comparisons}")
    print(f"comparison_seconds={comparison_seconds:.6f}")
    print(f"comparison_calls_per_second={comparisons / comparison_seconds:.2f}")
    print(f"distance_calls={comparisons}")
    print(f"distance_seconds={distance_seconds:.6f}")
    print(f"distance_calls_per_second={comparisons / distance_seconds:.2f}")


if __name__ == "__main__":
    main()
