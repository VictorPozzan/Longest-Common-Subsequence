import argparse
import shlex
import sys

from .benchmark import (
    ALGORITHM_DISPLAY,
    DEFAULT_DATASET,
    DEFAULT_FILE,
    DEFAULT_BENCHMARK_OUTPUT,
    DEFAULT_RUNS,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_WARMUP_RUNS,
    algorithm_choices,
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
        choices=algorithm_choices(),
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
        choices=algorithm_choices(),
        default=list(ALGORITHM_DISPLAY.keys()),
        help="Algorithms to execute.",
    )
    benchmark_parser.add_argument(
        "--output-csv",
        dest="output",
        help=argparse.SUPPRESS,
    )
    benchmark_parser.add_argument(
        "--output",
        default=str(DEFAULT_BENCHMARK_OUTPUT),
        help="Raw CSV file path for benchmark rows.",
    )
    benchmark_parser.add_argument(
        "--allow-slow",
        action="store_true",
        help="Run brute-force approaches even when the input is above the safety limit.",
    )
    benchmark_parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help="Number of measured runs per input and algorithm.",
    )
    benchmark_parser.add_argument(
        "--warmup-runs",
        type=int,
        default=DEFAULT_WARMUP_RUNS,
        help="Number of warmup runs per input and algorithm.",
    )
    benchmark_parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per-run timeout in seconds for benchmark subprocesses.",
    )

    return parser.parse_args(argv)


def main(argv=None, command_name="python -m lcs.cli"):
    args = parse_args(argv)
    argv_list = list(argv) if argv is not None else sys.argv[1:]
    command_text = command_name
    if argv_list:
        command_text = f"{command_text} {' '.join(shlex.quote(arg) for arg in argv_list)}"

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
            args.output,
            args.runs,
            args.warmup_runs,
            args.timeout_seconds,
            command_text=command_text,
        )
        return

    raise ValueError(f"Unknown command '{args.command}'.")


if __name__ == "__main__":
    main()
