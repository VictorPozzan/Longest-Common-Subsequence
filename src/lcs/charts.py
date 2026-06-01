from __future__ import annotations

import csv
from pathlib import Path

from .benchmark import ALGORITHM_DISPLAY


DEFAULT_SUMMARY_INPUT = Path("results/current/summary.csv")
DEFAULT_OUTPUT_DIR = Path("results/current/charts")
ALGORITHM_COLORS = {
    "dynamic_programming": "blue",
    "brute_force": "orange",
    "recursive_brute_force": "red",
}
CHART_FILENAMES = {
    "mean_time_seconds": "execution_time_by_input_size.png",
    "mean_comparisons": "comparisons_by_input_size.png",
    "lcs_length": "lcs_length_by_input_size.png",
}
CHART_SPECS = {
    "mean_time_seconds": {
        "title": "Execution Time by Input Size",
        "ylabel": "Mean execution time (seconds)",
        "yscale": "log",
    },
    "mean_comparisons": {
        "title": "Comparisons by Input Size",
        "ylabel": "Mean comparisons",
        "yscale": "linear",
    },
    "lcs_length": {
        "title": "LCS Length by Input Size",
        "ylabel": "LCS length",
        "yscale": "linear",
    },
}


def import_pyplot():
    try:
        import matplotlib
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "matplotlib is required to generate charts. "
            "Install it with `python -m pip install -e .[charts]`."
        ) from exc

    matplotlib.use("Agg")
    import matplotlib.pyplot as pyplot

    return pyplot


def read_summary_rows(input_path):
    summary_path = Path(input_path)

    with summary_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_completed_series(summary_rows):
    grouped = {algorithm: [] for algorithm in ALGORITHM_DISPLAY}

    for row in summary_rows:
        if row["status_summary"] != "completed":
            continue

        completed_runs = int(row["completed_runs"] or 0)
        if completed_runs <= 0:
            continue

        algorithm = row["algorithm"]
        if algorithm not in grouped:
            continue

        grouped[algorithm].append(
            {
                "input_name": row["input_name"],
                "input_size": max(int(row["input_size_a"]), int(row["input_size_b"])),
                "mean_time_seconds": float(row["mean_time_seconds"]),
                "mean_comparisons": float(row["mean_comparisons"]),
                "lcs_length": int(row["lcs_length"]),
            }
        )

    for series in grouped.values():
        series.sort(key=lambda item: (item["input_size"], item["input_name"]))

    return grouped


def build_chart_output_paths(output_dir):
    base_dir = Path(output_dir)
    return {
        metric: base_dir / filename for metric, filename in CHART_FILENAMES.items()
    }


def plot_metric_chart(pyplot, series_by_algorithm, metric, output_path):
    spec = CHART_SPECS[metric]
    figure, axis = pyplot.subplots(figsize=(10, 6))
    has_data = False

    for algorithm in ALGORITHM_DISPLAY:
        series = series_by_algorithm.get(algorithm, [])
        if not series:
            continue

        x_values = [point["input_size"] for point in series]
        y_values = [point[metric] for point in series]
        axis.plot(
            x_values,
            y_values,
            label=ALGORITHM_DISPLAY[algorithm],
            color=ALGORITHM_COLORS[algorithm],
            marker="o",
            linewidth=2,
            markersize=4,
        )
        has_data = True

    if not has_data:
        pyplot.close(figure)
        raise ValueError("No completed benchmark rows were available to plot.")

    axis.set_title(spec["title"])
    axis.set_xlabel("Input size")
    axis.set_ylabel(spec["ylabel"])
    axis.set_yscale(spec["yscale"])
    axis.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.6)
    axis.legend()

    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    pyplot.close(figure)


def generate_charts(input_path=DEFAULT_SUMMARY_INPUT, output_dir=DEFAULT_OUTPUT_DIR):
    summary_rows = read_summary_rows(input_path)
    series_by_algorithm = build_completed_series(summary_rows)
    output_paths = build_chart_output_paths(output_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    pyplot = import_pyplot()

    for metric, output_path in output_paths.items():
        plot_metric_chart(pyplot, series_by_algorithm, metric, output_path)

    return output_paths
