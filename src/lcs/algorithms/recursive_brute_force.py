from lcs.models import LCSResult


class BFRecursiveLCS:
    algorithm_name = "recursive_brute_force"

    def __init__(self):
        self.comp = 0

    def solve(self, string_a, string_b):
        self.comp = 0
        subsequence = self.lcs_recursive(string_a, string_b)

        return LCSResult(
            algorithm=self.algorithm_name,
            input_a=string_a,
            input_b=string_b,
            input_size_a=len(string_a),
            input_size_b=len(string_b),
            lcs=subsequence,
            lcs_length=len(subsequence),
            comparisons=self.comp,
        )

    def lcs(self, string_a, string_b):
        return self.solve(string_a, string_b)

    def lcs_recursive(self, string_a, string_b):
        self.comp += 1

        if not string_a or not string_b:
            return ""

        if string_a[-1] == string_b[-1]:
            return self.lcs_recursive(string_a[:-1], string_b[:-1]) + string_a[-1]

        left = self.lcs_recursive(string_a[:-1], string_b)
        right = self.lcs_recursive(string_a, string_b[:-1])

        if len(left) >= len(right):
            return left

        return right
