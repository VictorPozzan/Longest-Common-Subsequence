import tempfile
import unittest
from pathlib import Path

from Data import Data
from bfrecursive import BFRecursiveLCS
from bruteforce import BruteForceLCS
from dynamic import DynamicLCS


class DataTests(unittest.TestCase):
    def test_clean_data_removes_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("A B C\nA  C\n", encoding="utf-8")

            string_a, string_b = Data().cleanData(file_path)

        self.assertEqual(string_a, "ABC")
        self.assertEqual(string_b, "AC")


class AlgorithmTests(unittest.TestCase):
    def test_dynamic_and_bruteforce_match_known_case(self):
        string_a = "ABCBDAB"
        string_b = "BDCABA"

        dynamic_result = DynamicLCS().lcs(string_a, string_b)
        brute_force_result = BruteForceLCS().lcs(string_a, string_b)

        self.assertEqual(dynamic_result[0], 4)
        self.assertEqual(brute_force_result[0], 4)
        self.assertEqual(dynamic_result[0], brute_force_result[0])

    def test_recursive_algorithm_returns_valid_subsequence(self):
        string_a = "ABC"
        string_b = "AC"

        length, _, _, subsequence = BFRecursiveLCS().lcs(string_a, string_b)

        self.assertEqual(length, 2)
        self.assertEqual(subsequence, "AC")


if __name__ == "__main__":
    unittest.main()
