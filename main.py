import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import re

from Data import Data
from bfrecursive import BFRecursiveLCS
from bruteforce import BruteForceLCS
from dynamic import DynamicLCS


DEFAULT_FILE = Path("DataBase2/Strings02.txt")
ALGORITHM_DISPLAY = {
    "dynamic": "Dynamic programming",
    "bruteforce": "Brute force",
    "recursive": "Recursive brute force",
}
ALGORITHM_LIMITS = {
    "dynamic": None,
    "bruteforce": 18,
    "recursive": 12,
}


@dataclass
class RunResult:
    algorithm: str
    length: int
    elapsed_seconds: float
    comparisons: int
    subsequence: str
    status: str = "ok"
    message: str = ""


def build_algorithms():
    return {
        "dynamic": DynamicLCS,
        "bruteforce": BruteForceLCS,
        "recursive": BFRecursiveLCS,
    }


def parse_args():
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
        default="DataBase2",
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

    return parser.parse_args()


def natural_sort_key(path):
    parts = re.split(r"(\d+)", path.name)
    key = []

    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())

    return key


def load_sequences(file_path):
    data = Data()
    string_a, string_b = data.cleanData(file_path)
    return string_a, string_b


def run_algorithm(name, string_a, string_b, allow_slow):
    limit = ALGORITHM_LIMITS[name]
    input_size = max(len(string_a), len(string_b))

    if limit is not None and input_size > limit and not allow_slow:
        return RunResult(
            algorithm=name,
            length=0,
            elapsed_seconds=0.0,
            comparisons=0,
            subsequence="",
            status="skipped",
            message=f"Skipped because input length {input_size} exceeds the safe limit {limit}.",
        )

    algorithm = build_algorithms()[name]()
    length, elapsed_seconds, comparisons, subsequence = algorithm.lcs(
        string_a, string_b
    )

    return RunResult(
        algorithm=name,
        length=length,
        elapsed_seconds=elapsed_seconds,
        comparisons=comparisons,
        subsequence=subsequence,
    )


def compare_file(file_path, algorithm_names, allow_slow):
    string_a, string_b = load_sequences(file_path)
    results = [
        run_algorithm(name, string_a, string_b, allow_slow) for name in algorithm_names
    ]

    print(f"File: {file_path}")
    print(f"String A ({len(string_a)}): {string_a}")
    print(f"String B ({len(string_b)}): {string_b}")
    print("")
    print(format_results_table(results))

    valid_subsequences = [result.subsequence for result in results if result.status == "ok"]
    if valid_subsequences:
        print("")
        print(f"Representative LCS: {valid_subsequences[0]}")


def benchmark_dataset(dataset_path, algorithm_names, allow_slow, output_csv):
    dataset = Path(dataset_path)
    files = sorted(dataset.glob("*.txt"), key=natural_sort_key)

    if not files:
        raise FileNotFoundError(f"No .txt files found in '{dataset.as_posix()}'.")

    benchmark_rows = []

    for file_path in files:
        string_a, string_b = load_sequences(file_path)
        for name in algorithm_names:
            result = run_algorithm(name, string_a, string_b, allow_slow)
            benchmark_rows.append(
                {
                    "file": file_path.as_posix(),
                    "algorithm": name,
                    "len_a": len(string_a),
                    "len_b": len(string_b),
                    "lcs_length": result.length,
                    "elapsed_ms": f"{result.elapsed_seconds * 1000:.6f}",
                    "comparisons": result.comparisons,
                    "status": result.status,
                    "message": result.message,
                }
            )

    print(format_benchmark_table(benchmark_rows))

    if output_csv:
        export_csv(output_csv, benchmark_rows)
        print("")
        print(f"CSV exported to {output_csv}")


def format_results_table(results):
    rows = [
        [
            ALGORITHM_DISPLAY[result.algorithm],
            result.status.upper() if result.status != "ok" else result.subsequence or "-",
            str(result.length),
            str(result.comparisons),
            f"{result.elapsed_seconds * 1000:.6f}",
            result.message or "-",
        ]
        for result in results
    ]

    headers = ["Algorithm", "Subsequence", "Length", "Comparisons", "Time (ms)", "Notes"]
    return render_table(headers, rows)


def format_benchmark_table(benchmark_rows):
    rows = [
        [
            row["file"],
            ALGORITHM_DISPLAY[row["algorithm"]],
            str(row["len_a"]),
            str(row["len_b"]),
            str(row["lcs_length"]),
            row["elapsed_ms"],
            str(row["comparisons"]),
            row["status"],
        ]
        for row in benchmark_rows
    ]

    headers = ["File", "Algorithm", "Len A", "Len B", "LCS", "Time (ms)", "Comparisons", "Status"]
    return render_table(headers, rows)


def render_table(headers, rows):
    widths = [len(header) for header in headers]

    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    lines = []
    header_line = " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
    separator = "-+-".join("-" * widths[index] for index in range(len(headers)))

    lines.append(header_line)
    lines.append(separator)

    for row in rows:
        lines.append(
            " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))
        )

    return "\n".join(lines)


def export_csv(output_path, benchmark_rows):
    fieldnames = [
        "file",
        "algorithm",
        "len_a",
        "len_b",
        "lcs_length",
        "elapsed_ms",
        "comparisons",
        "status",
        "message",
    ]

    with Path(output_path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(benchmark_rows)


def main():
    args = parse_args()
    if args.command is None:
        compare_file(str(DEFAULT_FILE), list(ALGORITHM_DISPLAY.keys()), False)
        return

    command = args.command

    if command == "compare":
        compare_file(args.file, args.algorithms, args.allow_slow)
        return

    if command == "benchmark":
        benchmark_dataset(
            args.dataset,
            args.algorithms,
            args.allow_slow,
            args.output_csv,
        )
        return

    raise ValueError(f"Unknown command '{command}'.")


if __name__ == "__main__":
    main()
