import csv
from pathlib import Path
import re

from .algorithms import BFRecursiveLCS, BruteForceLCS, DynamicLCS
from .datasets import read_pair, resolve_path, to_repo_relative
from .models import RunResult


DEFAULT_FILE = Path("data/database2/Strings02.txt")
DEFAULT_DATASET = Path("data/database2")
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


def build_algorithms():
    return {
        "dynamic": DynamicLCS,
        "bruteforce": BruteForceLCS,
        "recursive": BFRecursiveLCS,
    }


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
    return read_pair(file_path)


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

    print(f"File: {to_repo_relative(resolve_path(file_path))}")
    print(f"String A ({len(string_a)}): {string_a}")
    print(f"String B ({len(string_b)}): {string_b}")
    print("")
    print(format_results_table(results))

    valid_subsequences = [result.subsequence for result in results if result.status == "ok"]
    if valid_subsequences:
        print("")
        print(f"Representative LCS: {valid_subsequences[0]}")


def benchmark_dataset(dataset_path, algorithm_names, allow_slow, output_csv):
    dataset = resolve_path(dataset_path)
    files = sorted(dataset.glob("*.txt"), key=natural_sort_key)

    if not files:
        raise FileNotFoundError(f"No .txt files found in '{to_repo_relative(dataset)}'.")

    benchmark_rows = []

    for file_path in files:
        string_a, string_b = load_sequences(file_path)
        for name in algorithm_names:
            result = run_algorithm(name, string_a, string_b, allow_slow)
            benchmark_rows.append(
                {
                    "file": to_repo_relative(file_path),
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

    output_file = Path(output_path)

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(benchmark_rows)
