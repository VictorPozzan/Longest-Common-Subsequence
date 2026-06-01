import argparse

from .benchmark import (
    ALGORITHM_DISPLAY,
    DEFAULT_DATASET,
    DEFAULT_FILE,
    benchmark_dataset,
    compare_file,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare Longest Common Subsequence strategies."
    )
    subparsers = parser.add_subparsers(dest="command")

    compare_parser = subparsers.add_parser(
        "compare",
        help="Run the selected algorithms for one input file.",
    )
    compare_parser.add_argument(
        "file",
        nargs="?",
        default=str(DEFAULT_FILE),
        help="Path to a file containing two sequences.",
    )
    compare_parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=list(ALGORITHM_DISPLAY.keys()),
        default=list(ALGORITHM_DISPLAY.keys()),
        help="Algorithms to execute.",
    )
    compare_parser.add_argument(
        "--allow-slow",
        action="store_true",
        help="Run brute-force approaches even when the input is above the safety limit.",
    )

    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Run a benchmark over all input files inside a dataset directory.",
    )
    benchmark_parser.add_argument(
        "dataset",
        nargs="?",
        default=str(DEFAULT_DATASET),
        help="Directory containing input files.",
    )
    benchmark_parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=list(ALGORITHM_DISPLAY.keys()),
        default=list(ALGORITHM_DISPLAY.keys()),
        help="Algorithms to execute.",
    )
    benchmark_parser.add_argument(
        "--output-csv",
        help="Optional CSV file path to export the benchmark results.",
    )
    benchmark_parser.add_argument(
        "--allow-slow",
        action="store_true",
        help="Run brute-force approaches even when the input is above the safety limit.",
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.command is None:
        compare_file(str(DEFAULT_FILE), list(ALGORITHM_DISPLAY.keys()), False)
        return

    if args.command == "compare":
        compare_file(args.file, args.algorithms, args.allow_slow)
        return

    if args.command == "benchmark":
        benchmark_dataset(
            args.dataset,
            args.algorithms,
            args.allow_slow,
            args.output_csv,
        )
        return

    raise ValueError(f"Unknown command '{args.command}'.")


if __name__ == "__main__":
    main()
