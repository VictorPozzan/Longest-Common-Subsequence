import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lcs.algorithms.brute_force import BruteForceLCS
from lcs.algorithms.dynamic_programming import DynamicLCS
from lcs.algorithms.recursive_brute_force import BFRecursiveLCS
from lcs.datasets import read_pair
from lcs.models import LCSResult


class DataTests(unittest.TestCase):
    def test_clean_data_removes_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("A B C\nA  C\n", encoding="utf-8")

            string_a, string_b = read_pair(file_path)

        self.assertEqual(string_a, "ABC")
        self.assertEqual(string_b, "AC")


class AlgorithmTests(unittest.TestCase):
    def assert_is_subsequence(self, candidate, sequence):
        index = 0

        for char in sequence:
            if index < len(candidate) and candidate[index] == char:
                index += 1

        self.assertEqual(index, len(candidate))

    def assert_valid_result(self, result, string_a, string_b, expected_length):
        self.assertIsInstance(result, LCSResult)
        self.assertEqual(result.input_a, string_a)
        self.assertEqual(result.input_b, string_b)
        self.assertEqual(result.input_size_a, len(string_a))
        self.assertEqual(result.input_size_b, len(string_b))
        self.assertEqual(result.lcs_length, expected_length)
        self.assertEqual(result.lcs_length, len(result.lcs))
        self.assertGreaterEqual(result.comparisons, 0)
        self.assert_is_subsequence(result.lcs, string_a)
        self.assert_is_subsequence(result.lcs, string_b)

    def test_dynamic_and_bruteforce_match_known_case(self):
        string_a = "ABCBDAB"
        string_b = "BDCABA"

        dynamic_result = DynamicLCS().solve(string_a, string_b)
        brute_force_result = BruteForceLCS().solve(string_a, string_b)

        self.assert_valid_result(dynamic_result, string_a, string_b, 4)
        self.assert_valid_result(brute_force_result, string_a, string_b, 4)
        self.assertEqual(dynamic_result.lcs_length, brute_force_result.lcs_length)

    def test_recursive_algorithm_returns_valid_subsequence(self):
        string_a = "ABC"
        string_b = "AC"

        result = BFRecursiveLCS().solve(string_a, string_b)

        self.assert_valid_result(result, string_a, string_b, 2)
        self.assertEqual(result.lcs, "AC")

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
            self.assert_valid_result(result, string_a, string_b, 3)
            actual_names.add(result.algorithm)

        self.assertEqual(actual_names, expected_names)


if __name__ == "__main__":
    unittest.main()
