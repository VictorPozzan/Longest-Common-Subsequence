from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from statistics import mean
import re
import subprocess
import sys
from time import perf_counter
from uuid import uuid4

from .algorithms import BFRecursiveLCS, BruteForceLCS, DynamicLCS
from .datasets import project_root, read_pair, resolve_path, to_repo_relative
from .models import LCSResult, TimedRunResult


DEFAULT_FILE = Path("data/database2/Strings02.txt")
DEFAULT_DATASET = Path("data/database2")
DEFAULT_BENCHMARK_OUTPUT = Path("results/current/benchmark.csv")
DEFAULT_RUNS = 6
DEFAULT_WARMUP_RUNS = 1
DEFAULT_TIMEOUT_SECONDS = 30.0
ALGORITHM_DISPLAY = {
    "dynamic_programming": "Dynamic programming",
    "brute_force": "Brute force",
    "recursive_brute_force": "Recursive brute force",
}
ALGORITHM_LIMITS = {
    "dynamic_programming": None,
    "brute_force": 18,
    "recursive_brute_force": 12,
}
ALGORITHM_ALIASES = {
    "dynamic": "dynamic_programming",
    "bruteforce": "brute_force",
    "recursive": "recursive_brute_force",
}
RAW_BENCHMARK_FIELDNAMES = [
    "run_id",
    "run_index",
    "is_warmup",
    "algorithm",
    "dataset",
    "input_name",
    "input_size_a",
    "input_size_b",
    "lcs_length",
    "execution_time_seconds",
    "comparisons",
    "status",
    "error",
    "timestamp",
]


def build_algorithms():
    return {
        "dynamic_programming": DynamicLCS,
        "brute_force": BruteForceLCS,
        "recursive_brute_force": BFRecursiveLCS,
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


def algorithm_choices():
    return list(ALGORITHM_DISPLAY.keys()) + list(ALGORITHM_ALIASES.keys())


def normalize_algorithm_name(name):
    if name in ALGORITHM_DISPLAY:
        return name

    if name in ALGORITHM_ALIASES:
        return ALGORITHM_ALIASES[name]

    raise ValueError(f"Unknown algorithm '{name}'.")


def normalize_algorithm_names(names):
    normalized_names = []

    for name in names:
        normalized_name = normalize_algorithm_name(name)
        if normalized_name not in normalized_names:
            normalized_names.append(normalized_name)

    return normalized_names


def create_lcs_result(name, string_a, string_b, payload):
    return LCSResult(
        algorithm=name,
        input_a=string_a,
        input_b=string_b,
        input_size_a=len(string_a),
        input_size_b=len(string_b),
        lcs=payload["lcs"],
        lcs_length=payload["lcs_length"],
        comparisons=payload["comparisons"],
    )


def should_skip_algorithm(name, string_a, string_b, allow_slow):
    normalized_name = normalize_algorithm_name(name)
    limit = ALGORITHM_LIMITS[normalized_name]
    input_size = max(len(string_a), len(string_b))

    if limit is None or allow_slow:
        return None

    if input_size > limit:
        return (
            normalized_name,
            f"Skipped because input length {input_size} exceeds the safe limit {limit}.",
        )

    return None


def execute_algorithm_in_process(name, string_a, string_b, allow_slow):
    skip_info = should_skip_algorithm(name, string_a, string_b, allow_slow)
    if skip_info is not None:
        normalized_name, message = skip_info
        return TimedRunResult(
            algorithm=normalized_name,
            elapsed_seconds=0.0,
            status="skipped_by_safety_limit",
            message=message,
        )

    normalized_name = normalize_algorithm_name(name)
    algorithm = build_algorithms()[normalized_name]()
    start = perf_counter()
    lcs_result = algorithm.solve(string_a, string_b)
    elapsed_seconds = perf_counter() - start

    return TimedRunResult(
        algorithm=normalized_name,
        elapsed_seconds=elapsed_seconds,
        lcs_result=lcs_result,
        status="completed",
    )


def run_algorithm_subprocess(name, file_path, string_a, string_b, timeout_seconds):
    normalized_name = normalize_algorithm_name(name)
    root = project_root()
    src_path = root / "src"
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(src_path)
    )

    command = [
        sys.executable,
        "-m",
        "lcs.benchmark_worker",
        "--algorithm",
        normalized_name,
        "--file",
        str(resolve_path(file_path)),
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
            cwd=str(root),
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return TimedRunResult(
            algorithm=normalized_name,
            elapsed_seconds=0.0,
            status="timeout",
            message=f"Timed out after {timeout_seconds} seconds.",
        )

    if completed.returncode != 0:
        error_text = completed.stderr.strip() or completed.stdout.strip() or (
            f"Worker exited with return code {completed.returncode}."
        )
        return TimedRunResult(
            algorithm=normalized_name,
            elapsed_seconds=0.0,
            status="error",
            message=error_text,
        )

    try:
        payload = json.loads(completed.stdout.strip())
    except json.JSONDecodeError as exc:
        return TimedRunResult(
            algorithm=normalized_name,
            elapsed_seconds=0.0,
            status="error",
            message=f"Invalid worker output: {exc}",
        )

    lcs_result = create_lcs_result(normalized_name, string_a, string_b, payload)
    return TimedRunResult(
        algorithm=normalized_name,
        elapsed_seconds=payload["elapsed_seconds"],
        lcs_result=lcs_result,
        status="completed",
    )


def build_benchmark_row(
    run_id,
    run_index,
    is_warmup,
    dataset,
    input_name,
    string_a,
    string_b,
    result,
):
    return {
        "run_id": run_id,
        "run_index": run_index,
        "is_warmup": is_warmup,
        "algorithm": result.algorithm,
        "dataset": dataset,
        "input_name": input_name,
        "input_size_a": len(string_a),
        "input_size_b": len(string_b),
        "lcs_length": result.length if result.status == "completed" else "",
        "execution_time_seconds": (
            f"{result.elapsed_seconds:.9f}" if result.status == "completed" else ""
        ),
        "comparisons": result.comparisons if result.status == "completed" else "",
        "status": result.status,
        "error": result.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def compare_file(file_path, algorithm_names, allow_slow):
    string_a, string_b = load_sequences(file_path)
    normalized_names = normalize_algorithm_names(algorithm_names)
    results = [
        execute_algorithm_in_process(name, string_a, string_b, allow_slow)
        for name in normalized_names
    ]

    print(f"File: {to_repo_relative(resolve_path(file_path))}")
    print(f"String A ({len(string_a)}): {string_a}")
    print(f"String B ({len(string_b)}): {string_b}")
    print("")
    print(format_results_table(results))

    valid_subsequences = [
        result.subsequence for result in results if result.status == "completed"
    ]
    if valid_subsequences:
        print("")
        print(f"Representative LCS: {valid_subsequences[0]}")


def benchmark_dataset(
    dataset_path,
    algorithm_names,
    allow_slow,
    output_path=DEFAULT_BENCHMARK_OUTPUT,
    runs=DEFAULT_RUNS,
    warmup_runs=DEFAULT_WARMUP_RUNS,
    timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
):
    dataset = resolve_path(dataset_path)
    files = sorted(dataset.glob("*.txt"), key=natural_sort_key)

    if not files:
        raise FileNotFoundError(f"No .txt files found in '{to_repo_relative(dataset)}'.")

    normalized_names = normalize_algorithm_names(algorithm_names)
    total_runs = warmup_runs + runs
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    dataset_label = to_repo_relative(dataset)
    benchmark_rows = []

    for file_path in files:
        string_a, string_b = load_sequences(file_path)
        input_name = file_path.name

        for name in normalized_names:
            skip_info = should_skip_algorithm(name, string_a, string_b, allow_slow)

            for run_index in range(1, total_runs + 1):
                is_warmup = run_index <= warmup_runs

                if skip_info is not None:
                    normalized_name, message = skip_info
                    result = TimedRunResult(
                        algorithm=normalized_name,
                        elapsed_seconds=0.0,
                        status="skipped_by_safety_limit",
                        message=message,
                    )
                else:
                    result = run_algorithm_subprocess(
                        name,
                        file_path,
                        string_a,
                        string_b,
                        timeout_seconds,
                    )

                benchmark_rows.append(
                    build_benchmark_row(
                        run_id=run_id,
                        run_index=run_index,
                        is_warmup=is_warmup,
                        dataset=dataset_label,
                        input_name=input_name,
                        string_a=string_a,
                        string_b=string_b,
                        result=result,
                    )
                )

    export_csv(output_path, benchmark_rows)
    print(format_benchmark_overview(benchmark_rows))
    print("")
    print(f"CSV exported to {output_path}")


def format_results_table(results):
    rows = [
        [
            ALGORITHM_DISPLAY[result.algorithm],
            result.status.upper()
            if result.status != "completed"
            else result.subsequence or "-",
            str(result.length),
            str(result.comparisons),
            f"{result.elapsed_seconds * 1000:.6f}",
            result.message or "-",
        ]
        for result in results
    ]

    headers = [
        "Algorithm",
        "Subsequence",
        "Length",
        "Comparisons",
        "Time (ms)",
        "Notes",
    ]
    return render_table(headers, rows)


def format_benchmark_overview(benchmark_rows):
    grouped = {}

    for row in benchmark_rows:
        key = (row["input_name"], row["algorithm"])
        grouped.setdefault(
            key,
            {
                "completed_times": [],
                "completed_comparisons": [],
                "warmups": 0,
                "timeouts": 0,
                "skipped": 0,
                "errors": 0,
            },
        )
        bucket = grouped[key]

        if row["is_warmup"]:
            bucket["warmups"] += 1

        if row["status"] == "completed":
            if not row["is_warmup"]:
                bucket["completed_times"].append(float(row["execution_time_seconds"]))
                bucket["completed_comparisons"].append(int(row["comparisons"]))
        elif row["status"] == "timeout":
            bucket["timeouts"] += 1
        elif row["status"] == "skipped_by_safety_limit":
            bucket["skipped"] += 1
        elif row["status"] == "error":
            bucket["errors"] += 1

    rows = []

    for key in sorted(grouped.keys()):
        input_name, algorithm = key
        bucket = grouped[key]
        completed_runs = len(bucket["completed_times"])
        avg_time = (
            f"{mean(bucket['completed_times']):.9f}"
            if bucket["completed_times"]
            else "-"
        )
        avg_comparisons = (
            f"{mean(bucket['completed_comparisons']):.2f}"
            if bucket["completed_comparisons"]
            else "-"
        )
        rows.append(
            [
                input_name,
                ALGORITHM_DISPLAY[algorithm],
                str(completed_runs),
                str(bucket["warmups"]),
                str(bucket["timeouts"]),
                str(bucket["skipped"]),
                str(bucket["errors"]),
                avg_time,
                avg_comparisons,
            ]
        )

    headers = [
        "Input",
        "Algorithm",
        "Completed",
        "Warmups",
        "Timeouts",
        "Skipped",
        "Errors",
        "Avg Time (s)",
        "Avg Comparisons",
    ]
    return render_table(headers, rows)


def render_table(headers, rows):
    widths = [len(header) for header in headers]

    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    lines = []
    header_line = " | ".join(
        header.ljust(widths[index]) for index, header in enumerate(headers)
    )
    separator = "-+-".join("-" * widths[index] for index in range(len(headers)))

    lines.append(header_line)
    lines.append(separator)

    for row in rows:
        lines.append(
            " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))
        )

    return "\n".join(lines)


def export_csv(output_path, benchmark_rows):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RAW_BENCHMARK_FIELDNAMES)
        writer.writeheader()
        writer.writerows(benchmark_rows)
