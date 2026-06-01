import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = Path(__file__).resolve().parent

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from lcs.algorithms.brute_force import BruteForceLCS
from lcs.algorithms.dynamic_programming import DynamicLCS
from lcs.algorithms.recursive_brute_force import BFRecursiveLCS
from lcs.datasets import read_pair
from helpers import assert_valid_result


class DataTests(unittest.TestCase):
    def test_clean_data_removes_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("A B C\nA  C\n", encoding="utf-8")

            string_a, string_b = read_pair(file_path)

        self.assertEqual(string_a, "ABC")
        self.assertEqual(string_b, "AC")


class AlgorithmTests(unittest.TestCase):
    def test_all_algorithms_pass_required_correctness_cases(self):
        cases = [
            ("ABCBDAB", "BDCABA", 4),
            ("ABC", "ABC", 3),
            ("ABC", "DEF", 0),
            ("", "ABC", 0),
            ("ABC", "", 0),
        ]
        algorithms = [DynamicLCS, BruteForceLCS, BFRecursiveLCS]

        for algorithm_class in algorithms:
            for string_a, string_b, expected_length in cases:
                with self.subTest(
                    algorithm=algorithm_class.__name__,
                    string_a=string_a,
                    string_b=string_b,
                ):
                    result = algorithm_class().solve(string_a, string_b)
                    assert_valid_result(
                        self,
                        result,
                        string_a,
                        string_b,
                        expected_length,
                    )

    def test_all_algorithms_use_standard_interface(self):
        string_a = "ABC"
        string_b = "ABC"
        algorithms = [DynamicLCS(), BruteForceLCS(), BFRecursiveLCS()]

        expected_names = {
            "dynamic_programming",
            "brute_force",
            "recursive_brute_force",
        }
        actual_names = set()

        for algorithm in algorithms:
            result = algorithm.solve(string_a, string_b)
            assert_valid_result(self, result, string_a, string_b, 3)
            actual_names.add(result.algorithm)

        self.assertEqual(actual_names, expected_names)


if __name__ == "__main__":
    unittest.main()
