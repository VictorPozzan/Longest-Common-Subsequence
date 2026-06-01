import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lcs.benchmark import (
    RAW_BENCHMARK_FIELDNAMES,
    benchmark_dataset,
    summarize_benchmark_rows,
)


class BenchmarkTests(unittest.TestCase):
    def create_dataset(self, directory, content):
        dataset = Path(directory) / "dataset"
        dataset.mkdir()
        file_path = dataset / "sample.txt"
        file_path.write_text(content, encoding="utf-8")
        return dataset

    def test_benchmark_writes_raw_schema_with_warmup_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            dataset = self.create_dataset(directory, "ABC\nABC\n")
            output = Path(directory) / "benchmark.csv"
            summary = Path(directory) / "summary.csv"
            environment = Path(directory) / "environment.md"

            benchmark_dataset(
                dataset,
                ["dynamic_programming"],
                allow_slow=False,
                output_path=output,
                runs=1,
                warmup_runs=1,
                timeout_seconds=5,
                command_text="python -m lcs.cli benchmark --dataset dataset",
            )

            with output.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            with summary.open("r", encoding="utf-8", newline="") as file:
                summary_rows = list(csv.DictReader(file))
            environment_text = environment.read_text(encoding="utf-8")

        self.assertEqual(list(rows[0].keys()), RAW_BENCHMARK_FIELDNAMES)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["run_index"], "1")
        self.assertEqual(rows[1]["run_index"], "2")
        self.assertEqual(rows[0]["is_warmup"], "True")
        self.assertEqual(rows[1]["is_warmup"], "False")
        self.assertEqual(rows[0]["status"], "completed")
        self.assertEqual(rows[1]["status"], "completed")
        self.assertEqual(rows[0]["algorithm"], "dynamic_programming")
        self.assertEqual(rows[1]["algorithm"], "dynamic_programming")
        self.assertEqual(len(summary_rows), 1)
        self.assertEqual(summary_rows[0]["completed_runs"], "1")
        self.assertEqual(summary_rows[0]["status_summary"], "completed")
        self.assertEqual(summary_rows[0]["mean_comparisons"], "9.00")
        self.assertEqual(summary_rows[0]["mean_time_seconds"], rows[1]["execution_time_seconds"])
        self.assertIn("Command: python -m lcs.cli benchmark --dataset dataset", environment_text)
        self.assertIn(f"Dataset: {dataset}", environment_text)
        self.assertIn("Runs per input: 1", environment_text)
        self.assertIn("Warmup runs: 1", environment_text)

    def test_benchmark_records_skipped_rows_for_safety_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            dataset = self.create_dataset(
                directory,
                "ABCDEFGHIJKLMNOPQRS\nABCDEFGHIJKLMNOPQRS\n",
            )
            output = Path(directory) / "benchmark.csv"
            summary = Path(directory) / "summary.csv"

            benchmark_dataset(
                dataset,
                ["brute_force"],
                allow_slow=False,
                output_path=output,
                runs=2,
                warmup_runs=1,
                timeout_seconds=5,
            )

            with output.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            with summary.open("r", encoding="utf-8", newline="") as file:
                summary_rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 3)
        self.assertTrue(
            all(row["status"] == "skipped_by_safety_limit" for row in rows)
        )
        self.assertTrue(all(row["execution_time_seconds"] == "" for row in rows))
        self.assertTrue(all(row["comparisons"] == "" for row in rows))
        self.assertEqual(len(summary_rows), 1)
        self.assertEqual(summary_rows[0]["status_summary"], "skipped_by_safety_limit")
        self.assertEqual(summary_rows[0]["completed_runs"], "0")

    def test_summary_ignores_warmup_status_when_timeouting_measured_runs(self):
        rows = [
            {
                "run_id": "run-1",
                "run_index": 1,
                "is_warmup": True,
                "algorithm": "dynamic_programming",
                "dataset": "data/database2",
                "input_name": "sample.txt",
                "input_size_a": 3,
                "input_size_b": 3,
                "lcs_length": 3,
                "execution_time_seconds": "0.001000000",
                "comparisons": 9,
                "status": "completed",
                "error": "",
                "timestamp": "2026-06-01T00:00:00+00:00",
            },
            {
                "run_id": "run-1",
                "run_index": 2,
                "is_warmup": False,
                "algorithm": "dynamic_programming",
                "dataset": "data/database2",
                "input_name": "sample.txt",
                "input_size_a": 3,
                "input_size_b": 3,
                "lcs_length": "",
                "execution_time_seconds": "",
                "comparisons": "",
                "status": "timeout",
                "error": "Timed out after 5 seconds.",
                "timestamp": "2026-06-01T00:00:01+00:00",
            },
        ]

        summary_rows = summarize_benchmark_rows(rows)

        self.assertEqual(len(summary_rows), 1)
        self.assertEqual(summary_rows[0]["status_summary"], "timeout")
        self.assertEqual(summary_rows[0]["completed_runs"], "0")


if __name__ == "__main__":
    unittest.main()
