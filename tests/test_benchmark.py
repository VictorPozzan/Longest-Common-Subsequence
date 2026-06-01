import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lcs.benchmark import RAW_BENCHMARK_FIELDNAMES, benchmark_dataset


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

            benchmark_dataset(
                dataset,
                ["dynamic_programming"],
                allow_slow=False,
                output_path=output,
                runs=1,
                warmup_runs=1,
                timeout_seconds=5,
            )

            with output.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

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

    def test_benchmark_records_skipped_rows_for_safety_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            dataset = self.create_dataset(
                directory,
                "ABCDEFGHIJKLMNOPQRS\nABCDEFGHIJKLMNOPQRS\n",
            )
            output = Path(directory) / "benchmark.csv"

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

        self.assertEqual(len(rows), 3)
        self.assertTrue(
            all(row["status"] == "skipped_by_safety_limit" for row in rows)
        )
        self.assertTrue(all(row["execution_time_seconds"] == "" for row in rows))
        self.assertTrue(all(row["comparisons"] == "" for row in rows))


if __name__ == "__main__":
    unittest.main()
