from __future__ import annotations

import argparse
from time import perf_counter

from phonodist import get_profile, pronunciation_distance

SOURCE = "ˈlʊftvafn̩ˌʃtʏt͡spʊŋkt"
TARGET = "lˈʊftvˌafənʃtˌʏt\u200dspʊŋkt"


def _measure(count: int, *, explain: bool) -> float:
    start = perf_counter()
    for _ in range(count):
        pronunciation_distance(SOURCE, TARGET, language="de-DE", explain=explain)
    return perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure warm phonodist throughput.")
    parser.add_argument("--count", type=int, default=1000)
    args = parser.parse_args()

    cold_start = perf_counter()
    get_profile("de-DE")
    cold_profile = perf_counter() - cold_start
    score_only = _measure(args.count, explain=False)
    explained = _measure(args.count, explain=True)

    print(f"profile_load_seconds={cold_profile:.6f}")
    print(f"score_only_calls={args.count}")
    print(f"score_only_seconds={score_only:.6f}")
    print(f"score_only_calls_per_second={args.count / score_only:.2f}")
    print(f"explain_seconds={explained:.6f}")
    print(f"explain_calls_per_second={args.count / explained:.2f}")


if __name__ == "__main__":
    main()
