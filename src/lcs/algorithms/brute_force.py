from itertools import combinations

from lcs.models import LCSResult


class BruteForceLCS:
    algorithm_name = "brute_force"

    def __init__(self):
        self.comp = 0

    def solve(self, string_a, string_b):
        self.comp = 0
        base, target = self._ordered_inputs(string_a, string_b)
        longest = ""

        for size in range(len(base), 0, -1):
            for indexes in combinations(range(len(base)), size):
                candidate = "".join(base[index] for index in indexes)
                if self.isSubSeq(candidate, target):
                    longest = candidate
                    return LCSResult(
                        algorithm=self.algorithm_name,
                        input_a=string_a,
                        input_b=string_b,
                        input_size_a=len(string_a),
                        input_size_b=len(string_b),
                        lcs=longest,
                        lcs_length=len(longest),
                        comparisons=self.comp,
                    )

        return LCSResult(
            algorithm=self.algorithm_name,
            input_a=string_a,
            input_b=string_b,
            input_size_a=len(string_a),
            input_size_b=len(string_b),
            lcs=longest,
            lcs_length=0,
            comparisons=self.comp,
        )

    def lcs(self, string_a, string_b):
        return self.solve(string_a, string_b)

    def isSubSeq(self, sub, target):
        if not sub:
            return True

        sub_index = 0

        for char in target:
            self.comp += 1
            if sub[sub_index] == char:
                sub_index += 1
                if sub_index == len(sub):
                    return True

        return False

    def _ordered_inputs(self, string_a, string_b):
        if len(string_a) <= len(string_b):
            return string_a, string_b

        return string_b, string_a
