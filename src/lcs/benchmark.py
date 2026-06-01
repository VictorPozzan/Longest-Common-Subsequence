from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
from statistics import mean, median
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
SUMMARY_FIELDNAMES = [
    "dataset",
    "algorithm",
    "input_name",
    "input_size_a",
    "input_size_b",
    "completed_runs",
    "mean_time_seconds",
    "median_time_seconds",
    "min_time_seconds",
    "max_time_seconds",
    "mean_comparisons",
    "lcs_length",
    "status_summary",
]


def build_algorithms():
    return {
        "dynamic_programming": DynamicLCS,
        "brute_force": BruteForceLCS,
        "recursive_brute_force": BFRecursiveLCS,
    }


def benchmark_safety_limits():
    return {
        "dynamic_programming": "none",
        "brute_force": ALGORITHM_LIMITS["brute_force"],
        "recursive_brute_force": ALGORITHM_LIMITS["recursive_brute_force"],
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
    command_text=None,
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
    summary_rows = summarize_benchmark_rows(benchmark_rows)
    summary_path = Path(output_path).with_name("summary.csv")
    export_summary_csv(summary_path, summary_rows)
    environment_path = Path(output_path).with_name("environment.md")
    export_environment_report(
        environment_path=environment_path,
        benchmark_output_path=output_path,
        dataset=dataset_label,
        algorithm_names=normalized_names,
        runs=runs,
        warmup_runs=warmup_runs,
        timeout_seconds=timeout_seconds,
        allow_slow=allow_slow,
        command_text=command_text,
    )
    print(format_benchmark_overview(benchmark_rows))
    print("")
    print(f"CSV exported to {output_path}")
    print(f"Summary exported to {summary_path}")
    print(f"Environment exported to {environment_path}")


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


def summarize_benchmark_rows(benchmark_rows):
    grouped = {}

    for row in benchmark_rows:
        key = (
            row["dataset"],
            row["algorithm"],
            row["input_name"],
            row["input_size_a"],
            row["input_size_b"],
        )
        grouped.setdefault(
            key,
            {
                "completed_times": [],
                "completed_comparisons": [],
                "lcs_lengths": [],
                "eligible_statuses": [],
            },
        )
        bucket = grouped[key]

        if row["is_warmup"]:
            continue

        bucket["eligible_statuses"].append(row["status"])

        if row["status"] == "completed":
            bucket["completed_times"].append(float(row["execution_time_seconds"]))
            bucket["completed_comparisons"].append(int(row["comparisons"]))
            bucket["lcs_lengths"].append(int(row["lcs_length"]))

    summary_rows = []

    for key in sorted(grouped.keys()):
        dataset, algorithm, input_name, input_size_a, input_size_b = key
        bucket = grouped[key]
        completed_runs = len(bucket["completed_times"])

        if completed_runs > 0:
            status_summary = "completed"
            mean_time = f"{mean(bucket['completed_times']):.9f}"
            median_time_value = f"{median(bucket['completed_times']):.9f}"
            min_time = f"{min(bucket['completed_times']):.9f}"
            max_time = f"{max(bucket['completed_times']):.9f}"
            mean_comparisons = f"{mean(bucket['completed_comparisons']):.2f}"
            lcs_length = str(bucket["lcs_lengths"][0])
        elif bucket["eligible_statuses"] and all(
            status == "skipped_by_safety_limit"
            for status in bucket["eligible_statuses"]
        ):
            status_summary = "skipped_by_safety_limit"
            mean_time = ""
            median_time_value = ""
            min_time = ""
            max_time = ""
            mean_comparisons = ""
            lcs_length = ""
        elif bucket["eligible_statuses"] and all(
            status == "timeout" for status in bucket["eligible_statuses"]
        ):
            status_summary = "timeout"
            mean_time = ""
            median_time_value = ""
            min_time = ""
            max_time = ""
            mean_comparisons = ""
            lcs_length = ""
        else:
            status_summary = "error"
            mean_time = ""
            median_time_value = ""
            min_time = ""
            max_time = ""
            mean_comparisons = ""
            lcs_length = ""

        summary_rows.append(
            {
                "dataset": dataset,
                "algorithm": algorithm,
                "input_name": input_name,
                "input_size_a": input_size_a,
                "input_size_b": input_size_b,
                "completed_runs": str(completed_runs),
                "mean_time_seconds": mean_time,
                "median_time_seconds": median_time_value,
                "min_time_seconds": min_time,
                "max_time_seconds": max_time,
                "mean_comparisons": mean_comparisons,
                "lcs_length": lcs_length,
                "status_summary": status_summary,
            }
        )

    return summary_rows


def export_summary_csv(output_path, summary_rows):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDNAMES)
        writer.writeheader()
        writer.writerows(summary_rows)


def export_environment_report(
    environment_path,
    benchmark_output_path,
    dataset,
    algorithm_names,
    runs,
    warmup_runs,
    timeout_seconds,
    allow_slow,
    command_text=None,
):
    output_file = Path(environment_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    command_value = command_text or "Unavailable"
    git_commit = get_git_commit()
    memory_text = get_memory_text()
    safety_limits = benchmark_safety_limits()

    content = "\n".join(
        [
            "# Benchmark environment",
            "",
            f"Date: {datetime.now(timezone.utc).isoformat()}",
            f"Git commit: {git_commit}",
            f"OS: {platform.platform()}",
            f"CPU: {platform.processor() or platform.machine() or 'Unavailable'}",
            f"RAM: {memory_text}",
            f"Python version: {sys.version.split()[0]}",
            f"Command: {command_value}",
            f"Dataset: {dataset}",
            f"Algorithms: {', '.join(algorithm_names)}",
            f"Runs per input: {runs}",
            f"Warmup runs: {warmup_runs}",
            f"Timeout: {timeout_seconds} seconds",
            f"Safety limits: {json.dumps(safety_limits)}",
            f"Allow slow: {allow_slow}",
            f"Raw benchmark file: {Path(benchmark_output_path).name}",
            "Summary file: summary.csv",
        ]
    )

    output_file.write_text(content + "\n", encoding="utf-8")


def get_git_commit():
    root = project_root()
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except OSError:
        return "Unavailable"

    if completed.returncode != 0:
        return "Unavailable"

    return completed.stdout.strip() or "Unavailable"


def get_memory_text():
    if hasattr(os, "sysconf"):
        try:
            page_size = os.sysconf("SC_PAGE_SIZE")
            pages = os.sysconf("SC_PHYS_PAGES")
            total_bytes = page_size * pages
            return format_bytes(total_bytes)
        except (ValueError, OSError, AttributeError):
            pass

    if sys.platform.startswith("win"):
        try:
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("length", ctypes.c_ulong),
                    ("memory_load", ctypes.c_ulong),
                    ("total_phys", ctypes.c_ulonglong),
                    ("avail_phys", ctypes.c_ulonglong),
                    ("total_page_file", ctypes.c_ulonglong),
                    ("avail_page_file", ctypes.c_ulonglong),
                    ("total_virtual", ctypes.c_ulonglong),
                    ("avail_virtual", ctypes.c_ulonglong),
                    ("avail_extended_virtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatus()
            status.length = ctypes.sizeof(MemoryStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return format_bytes(status.total_phys)
        except Exception:
            pass

    return "Unavailable"


def format_bytes(total_bytes):
    gib = 1024 ** 3
    mib = 1024 ** 2

    if total_bytes >= gib:
        return f"{total_bytes / gib:.2f} GiB"

    return f"{total_bytes / mib:.2f} MiB"
