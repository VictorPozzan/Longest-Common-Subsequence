from __future__ import annotations

import argparse
import json
from time import perf_counter

from .benchmark import build_algorithms, normalize_algorithm_name
from .datasets import read_pair


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Internal worker for running one LCS algorithm in isolation."
    )
    parser.add_argument("--algorithm", required=True)
    parser.add_argument("--file", required=True)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    algorithm_name = normalize_algorithm_name(args.algorithm)
    string_a, string_b = read_pair(args.file)
    algorithm = build_algorithms()[algorithm_name]()

    start = perf_counter()
    result = algorithm.solve(string_a, string_b)
    elapsed_seconds = perf_counter() - start

    print(
        json.dumps(
            {
                "algorithm": result.algorithm,
                "lcs": result.lcs,
                "lcs_length": result.lcs_length,
                "comparisons": result.comparisons,
                "elapsed_seconds": elapsed_seconds,
            }
        )
    )


if __name__ == "__main__":
    main()
