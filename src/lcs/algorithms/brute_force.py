from itertools import combinations
from time import perf_counter


class BruteForceLCS:
    def __init__(self):
        self.comp = 0

    def lcs(self, string_a, string_b):
        self.comp = 0
        start = perf_counter()

        base, target = self._ordered_inputs(string_a, string_b)
        longest = ""

        for size in range(len(base), 0, -1):
            for indexes in combinations(range(len(base)), size):
                candidate = "".join(base[index] for index in indexes)
                if self.isSubSeq(candidate, target):
                    longest = candidate
                    execution_time = perf_counter() - start
                    return len(longest), execution_time, self.comp, longest

        execution_time = perf_counter() - start
        return 0, execution_time, self.comp, longest

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
