import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lcs.charts import build_chart_output_paths, build_completed_series, read_summary_rows


class ChartTests(unittest.TestCase):
    def test_read_summary_rows_and_filter_completed_series(self):
        with tempfile.TemporaryDirectory() as directory:
            summary_path = Path(directory) / "summary.csv"

            with summary_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
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
                    ],
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "dataset": "data/database2",
                            "algorithm": "dynamic_programming",
                            "input_name": "Strings03.txt",
                            "input_size_a": "3",
                            "input_size_b": "3",
                            "completed_runs": "6",
                            "mean_time_seconds": "0.000020000",
                            "median_time_seconds": "0.000019000",
                            "min_time_seconds": "0.000018000",
                            "max_time_seconds": "0.000022000",
                            "mean_comparisons": "9.00",
                            "lcs_length": "1",
                            "status_summary": "completed",
                        },
                        {
                            "dataset": "data/database2",
                            "algorithm": "dynamic_programming",
                            "input_name": "Strings02.txt",
                            "input_size_a": "2",
                            "input_size_b": "2",
                            "completed_runs": "6",
                            "mean_time_seconds": "0.000010000",
                            "median_time_seconds": "0.000009000",
                            "min_time_seconds": "0.000008000",
                            "max_time_seconds": "0.000012000",
                            "mean_comparisons": "4.00",
                            "lcs_length": "1",
                            "status_summary": "completed",
                        },
                        {
                            "dataset": "data/database2",
                            "algorithm": "brute_force",
                            "input_name": "Strings19.txt",
                            "input_size_a": "19",
                            "input_size_b": "19",
                            "completed_runs": "0",
                            "mean_time_seconds": "",
                            "median_time_seconds": "",
                            "min_time_seconds": "",
                            "max_time_seconds": "",
                            "mean_comparisons": "",
                            "lcs_length": "",
                            "status_summary": "skipped_by_safety_limit",
                        },
                    ]
                )

            rows = read_summary_rows(summary_path)
            series = build_completed_series(rows)

        self.assertEqual(len(rows), 3)
        self.assertEqual([point["input_size"] for point in series["dynamic_programming"]], [2, 3])
        self.assertEqual(series["dynamic_programming"][0]["mean_comparisons"], 4.0)
        self.assertEqual(series["brute_force"], [])

    def test_build_chart_output_paths_uses_stable_filenames(self):
        output_paths = build_chart_output_paths("results/current/charts")

        self.assertEqual(
            output_paths["mean_time_seconds"].as_posix(),
            "results/current/charts/execution_time_by_input_size.png",
        )
        self.assertEqual(
            output_paths["mean_comparisons"].as_posix(),
            "results/current/charts/comparisons_by_input_size.png",
        )
        self.assertEqual(
            output_paths["lcs_length"].as_posix(),
            "results/current/charts/lcs_length_by_input_size.png",
        )


if __name__ == "__main__":
    unittest.main()
